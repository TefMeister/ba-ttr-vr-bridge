// d3d11_probe.cpp -- a PROBE for desk runs, off unless BRIDGE_DESK_D3D11_PROBE=1 is in the game's environment.
//
// Question it answers (2026-11-12): in the OpenXR Simulator the VR mod counts every eye as shown, yet the headset's
// picture never changes. So what does the last copy into the headset's picture look like from inside Direct3D 11?
// It watches three calls on every Direct3D 11 context in the game's process and writes what it sees to
// bridge_desk.log: each NEW kind of copy once (who copies what into what, sizes, formats, which device each picture
// belongs to), a count of each kind every few seconds, and the fence waits. It changes nothing: every call is passed
// on exactly as it came.
#include <windows.h>
#include <d3d11_4.h>
#include <cstdio>
#include <cstring>

void log_line(const char* fmt, ...);
bool patch_named_import(HMODULE mod, const char* name, void* hook, void** real);
void shareable_on_device(ID3D11Device* dev);  // shareable.cpp

namespace {
// Positions of the calls in the context's method table (fixed by the Direct3D 11 headers).
const int kSlotCopySubresourceRegion = 46;
const int kSlotCopyResource = 47;
const int kSlotCopySubresourceRegion1 = 115; // ID3D11DeviceContext1
const int kSlotWait = 148;                 // ID3D11DeviceContext4::Wait
const DWORD kSummaryEveryMs = 5000;
const int kSummaries = 24;                 // two minutes of counts, then silence
const int kMaxKinds = 96;
const UINT kBigPicture = 4096;          // the eye pictures of this run: name the very pictures of their copies
const LONG kPairsPerKind = 14;

struct Kind {
    bool region;
    DWORD thread;
    void* ctxDevice;
    void* dstDevice;
    void* srcDevice;
    UINT dw, dh, dfmt, dusage, dbind, dmisc;
    UINT sw, sh, sfmt, susage, sbind, smisc;
    UINT dx, dy, bw, bh;
    bool hasBox;
    LONG count;
    void* lastDst;
    LONG distinctDst;
    LONG pairsLogged;
};

CRITICAL_SECTION g_lock;
Kind g_kinds[kMaxKinds];
int g_kindCount = 0;
LONG g_waits = 0, g_waitKinds = 0;
void* g_lastFence = nullptr;
UINT64 g_lastWaitValue = 0;

typedef void(STDMETHODCALLTYPE* CopyRegion_t)(ID3D11DeviceContext*, ID3D11Resource*, UINT, UINT, UINT, UINT,
                                               ID3D11Resource*, UINT, const D3D11_BOX*);
typedef void(STDMETHODCALLTYPE* CopyResource_t)(ID3D11DeviceContext*, ID3D11Resource*, ID3D11Resource*);
typedef HRESULT(STDMETHODCALLTYPE* Wait_t)(ID3D11DeviceContext4*, ID3D11Fence*, UINT64);
CopyRegion_t g_realRegion = nullptr;
CopyResource_t g_realResource = nullptr;
Wait_t g_realWait = nullptr;

void describe(ID3D11Resource* r, void** device, UINT* w, UINT* h, UINT* fmt, UINT* usage, UINT* bind, UINT* misc) {
    *device = nullptr;
    *w = *h = *fmt = *usage = *bind = *misc = 0;
    if (!r) return;
    ID3D11Device* d = nullptr;
    r->GetDevice(&d);
    *device = d;
    if (d) d->Release();
    ID3D11Texture2D* t = nullptr;
    if (SUCCEEDED(r->QueryInterface(__uuidof(ID3D11Texture2D), reinterpret_cast<void**>(&t))) && t) {
        D3D11_TEXTURE2D_DESC desc;
        t->GetDesc(&desc);
        *w = desc.Width; *h = desc.Height; *fmt = desc.Format;
        *usage = desc.Usage; *bind = desc.BindFlags; *misc = desc.MiscFlags;
        t->Release();
    }
}

void note(bool region, ID3D11DeviceContext* ctx, ID3D11Resource* dst, UINT dx, UINT dy, ID3D11Resource* src,
          const D3D11_BOX* box) {
    Kind k = {};
    k.region = region;
    k.thread = GetCurrentThreadId();
    ID3D11Device* cd = nullptr;
    ctx->GetDevice(&cd);
    k.ctxDevice = cd;
    if (cd) cd->Release();
    describe(dst, &k.dstDevice, &k.dw, &k.dh, &k.dfmt, &k.dusage, &k.dbind, &k.dmisc);
    describe(src, &k.srcDevice, &k.sw, &k.sh, &k.sfmt, &k.susage, &k.sbind, &k.smisc);
    k.dx = dx; k.dy = dy;
    k.hasBox = box != nullptr;
    if (box) { k.bw = box->right - box->left; k.bh = box->bottom - box->top; }
    if (k.dw < 256 && k.sw < 256) return;  // small pictures (icons, panels' helpers) are not the question

    EnterCriticalSection(&g_lock);
    int found = -1;
    for (int i = 0; i < g_kindCount; ++i) {
        const Kind& o = g_kinds[i];
        if (o.region == k.region && o.thread == k.thread && o.ctxDevice == k.ctxDevice && o.dw == k.dw &&
            o.dh == k.dh && o.dfmt == k.dfmt && o.sw == k.sw && o.sh == k.sh && o.sfmt == k.sfmt &&
            o.susage == k.susage && o.dx == k.dx && o.dy == k.dy && o.bw == k.bw && o.bh == k.bh &&
            o.dmisc == k.dmisc && o.smisc == k.smisc) {
            found = i;
            break;
        }
    }
    bool fresh = false;
    if (found < 0 && g_kindCount < kMaxKinds) {
        found = g_kindCount++;
        g_kinds[found] = k;
        fresh = true;
    }
    if (found >= 0) {
        Kind& o = g_kinds[found];
        ++o.count;
        if (o.lastDst != dst) { o.lastDst = dst; ++o.distinctDst; }
    }
    bool pair = false;
    if (found >= 0 && k.dw >= kBigPicture && g_kinds[found].pairsLogged < kPairsPerKind) {
        ++g_kinds[found].pairsLogged;
        pair = true;
    }
    LeaveCriticalSection(&g_lock);
    if (pair) log_line("[d3d11] kind %d call: INTO picture %p FROM picture %p", found, dst, src);
    if (fresh)
        log_line("[d3d11] copy kind %d: %s thread %lu ctx-device %p | INTO %ux%u fmt %u usage %u bind 0x%X misc 0x%X "
                 "device %p at (%u,%u) | FROM %ux%u fmt %u usage %u bind 0x%X misc 0x%X device %p box %s %ux%u%s%s",
                 found, region ? "CopySubresourceRegion" : "CopyResource", k.thread, k.ctxDevice, k.dw, k.dh, k.dfmt,
                 k.dusage, k.dbind, k.dmisc, k.dstDevice, k.dx, k.dy, k.sw, k.sh, k.sfmt, k.susage, k.sbind, k.smisc,
                 k.srcDevice, k.hasBox ? "yes" : "no", k.bw, k.bh,
                 (k.dstDevice != k.ctxDevice || k.srcDevice != k.ctxDevice) ? " | ANOTHER DEVICE'S PICTURE" : "",
                 (k.dfmt != k.sfmt) ? " | formats differ" : "");
}

void STDMETHODCALLTYPE hook_region(ID3D11DeviceContext* ctx, ID3D11Resource* dst, UINT dsub, UINT dx, UINT dy, UINT dz,
                                   ID3D11Resource* src, UINT ssub, const D3D11_BOX* box) {
    note(true, ctx, dst, dx, dy, src, box);
    g_realRegion(ctx, dst, dsub, dx, dy, dz, src, ssub, box);
}

void STDMETHODCALLTYPE hook_resource(ID3D11DeviceContext* ctx, ID3D11Resource* dst, ID3D11Resource* src) {
    note(false, ctx, dst, 0, 0, src, nullptr);
    g_realResource(ctx, dst, src);
}

HRESULT STDMETHODCALLTYPE hook_wait(ID3D11DeviceContext4* ctx, ID3D11Fence* fence, UINT64 value) {
    HRESULT hr = g_realWait(ctx, fence, value);
    LONG n = InterlockedIncrement(&g_waits);
    UINT64 done = fence ? fence->GetCompletedValue() : 0;
    if (n <= 6 || fence != g_lastFence || FAILED(hr)) {
        if (InterlockedIncrement(&g_waitKinds) <= 12)
            log_line("[d3d11] Wait #%ld: fence %p for value %llu (the fence stands at %llu) thread %lu -> 0x%08lX", n,
                     fence, value, done, GetCurrentThreadId(), hr);
    }
    g_lastFence = fence;
    g_lastWaitValue = value;
    return hr;
}

// Hook a Direct3D 11 routine at its own first bytes, so every caller is seen whatever method table it came through.
// Only done when the routine starts with the standard five bytes Windows keeps free for this; else it is left alone.
void* detour(void* fn, void* hook, const char* what, void** real) {
    static const BYTE kPrologue[5] = {0x8B, 0xFF, 0x55, 0x8B, 0xEC};
    BYTE* p = static_cast<BYTE*>(fn);
    if (p[0] == 0xE9) {  // an existing jump (another tool got there first): leave it
        log_line("[d3d11] %s: already redirected by something else, not watched", what);
        return nullptr;
    }
    if (memcmp(p, kPrologue, 5) != 0) {
        log_line("[d3d11] %s: unusual first bytes %02X %02X %02X %02X %02X, not watched", what, p[0], p[1], p[2], p[3], p[4]);
        return nullptr;
    }
    BYTE* tramp = static_cast<BYTE*>(VirtualAlloc(nullptr, 16, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE));
    if (!tramp) return nullptr;
    memcpy(tramp, p, 5);
    tramp[5] = 0xE9;
    *reinterpret_cast<INT32*>(tramp + 6) = static_cast<INT32>((p + 5) - (tramp + 10));
    DWORD old = 0;
    if (!VirtualProtect(p, 5, PAGE_EXECUTE_READWRITE, &old)) return nullptr;
    *real = tramp;  // before the jump is written: a call may come the very next moment
    p[0] = 0xE9;
    *reinterpret_cast<INT32*>(p + 1) = static_cast<INT32>(static_cast<BYTE*>(hook) - (p + 5));
    VirtualProtect(p, 5, old, &old);
    FlushInstructionCache(GetCurrentProcess(), p, 5);
    return tramp;
}

typedef void(STDMETHODCALLTYPE* CopyRegion1_t)(ID3D11DeviceContext1*, ID3D11Resource*, UINT, UINT, UINT, UINT,
                                                ID3D11Resource*, UINT, const D3D11_BOX*, UINT);
CopyRegion1_t g_realRegion1 = nullptr;
void STDMETHODCALLTYPE hook_region1(ID3D11DeviceContext1* ctx, ID3D11Resource* dst, UINT dsub, UINT dx, UINT dy, UINT dz,
                                    ID3D11Resource* src, UINT ssub, const D3D11_BOX* box, UINT flags) {
    note(true, ctx, dst, dx, dy, src, box);
    g_realRegion1(ctx, dst, dsub, dx, dy, dz, src, ssub, box, flags);
}

typedef HRESULT(WINAPI* Create_t)(IDXGIAdapter*, D3D_DRIVER_TYPE, HMODULE, UINT, const D3D_FEATURE_LEVEL*, UINT, UINT,
                                  ID3D11Device**, D3D_FEATURE_LEVEL*, ID3D11DeviceContext**);
Create_t g_realCreate = nullptr;
bool g_hooked = false;
bool g_watch = false;

void* slot_code(void* iface, int slot) { return (*reinterpret_cast<void***>(iface))[slot]; }

HRESULT WINAPI hook_create(IDXGIAdapter* adapter, D3D_DRIVER_TYPE type, HMODULE sw, UINT flags,
                           const D3D_FEATURE_LEVEL* levels, UINT nLevels, UINT sdk, ID3D11Device** dev,
                           D3D_FEATURE_LEVEL* got, ID3D11DeviceContext** ctx) {
    HRESULT hr = g_realCreate(adapter, type, sw, flags, levels, nLevels, sdk, dev, got, ctx);
    log_line("[d3d11] D3D11CreateDevice by the VR mod: flags 0x%X -> 0x%08lX, device %p, context %p", flags, hr,
             dev ? *dev : nullptr, ctx ? *ctx : nullptr);
    if (SUCCEEDED(hr) && dev && *dev) shareable_on_device(*dev);
    if (g_watch && SUCCEEDED(hr) && ctx && *ctx && !g_hooked) {
        g_hooked = true;
        ID3D11DeviceContext4* c4 = nullptr;
        (*ctx)->QueryInterface(__uuidof(ID3D11DeviceContext4), reinterpret_cast<void**>(&c4));
        void* fRegion = slot_code(*ctx, kSlotCopySubresourceRegion);
        void* fResource = slot_code(*ctx, kSlotCopyResource);
        void* fRegion1 = c4 ? slot_code(c4, kSlotCopySubresourceRegion1) : nullptr;
        void* fWait = c4 ? slot_code(c4, kSlotWait) : nullptr;
        HMODULE owner = nullptr;
        char name[MAX_PATH] = "?";
        if (GetModuleHandleExA(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS | GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
                               static_cast<LPCSTR>(fRegion), &owner) && owner)
            GetModuleFileNameA(owner, name, MAX_PATH);
        const char* leaf = strrchr(name, '\\');
        log_line("[d3d11] the context's copy routine lives in %s", leaf ? leaf + 1 : name);
        detour(fRegion, &hook_region, "CopySubresourceRegion", reinterpret_cast<void**>(&g_realRegion));
        detour(fResource, &hook_resource, "CopyResource", reinterpret_cast<void**>(&g_realResource));
        if (fRegion1 && fRegion1 != fRegion)
            detour(fRegion1, &hook_region1, "CopySubresourceRegion1", reinterpret_cast<void**>(&g_realRegion1));
        if (fWait) detour(fWait, &hook_wait, "Wait", reinterpret_cast<void**>(&g_realWait));
        log_line("[d3d11] watched at the routine itself: copies %d, whole-picture copies %d, copies(1) %d, fence waits %d",
                 g_realRegion != nullptr, g_realResource != nullptr, g_realRegion1 != nullptr, g_realWait != nullptr);
        if (c4) c4->Release();
    }
    return hr;
}

// TTWVR 1.0.0 build 6AF014A8 only: the four rows of six pictures the upscaler bridge keeps on the headset's device
// (found by reading the DLL on disk). Says how big each really is, which is what the mod's last copy checks.
const DWORD kKnownBuild = 0x6AF014A8;
const DWORD kPictureRowsRva = 0x1366280;
const int kPictureSlots = 24;
HMODULE g_vrMod = nullptr;

bool describe_guarded(void* candidate, int slot) {
    __try {
        void* device = nullptr;
        UINT w, h, fmt, usage, bind, misc;
        describe(static_cast<ID3D11Resource*>(candidate), &device, &w, &h, &fmt, &usage, &bind, &misc);
        log_line("[d3d11] bridge picture slot %d (row %d): %p is %ux%u fmt %u usage %u bind 0x%X misc 0x%X device %p", slot,
                 slot / 6, candidate, w, h, fmt, usage, bind, misc, device);
        return true;
    } __except (EXCEPTION_EXECUTE_HANDLER) {
        log_line("[d3d11] bridge picture slot %d: %p is not a Direct3D 11 picture", slot, candidate);
        return false;
    }
}

void dump_bridge_pictures() {
    if (!g_vrMod) return;
    BYTE* base = reinterpret_cast<BYTE*>(g_vrMod);
    auto nt = reinterpret_cast<IMAGE_NT_HEADERS*>(base + reinterpret_cast<IMAGE_DOS_HEADER*>(base)->e_lfanew);
    if (nt->FileHeader.TimeDateStamp != kKnownBuild) {
        log_line("[d3d11] another build of the VR mod: its picture rows are not known, not read");
        return;
    }
    void** rows = reinterpret_cast<void**>(base + kPictureRowsRva);
    for (int i = 0; i < kPictureSlots; ++i)
        if (rows[i]) describe_guarded(rows[i], i);
}

DWORD WINAPI probe_thread(LPVOID) {
    for (int s = 0; s < kSummaries; ++s) {
        Sleep(kSummaryEveryMs);
        if (s == 5 || s == 9) dump_bridge_pictures();
        char line[1800];
        int at = 0;
        EnterCriticalSection(&g_lock);
        for (int i = 0; i < g_kindCount && at < 1700; ++i) {
            at += sprintf_s(line + at, sizeof(line) - at, " k%d=%ld(%ld pictures)", i, g_kinds[i].count,
                            g_kinds[i].distinctDst);
            g_kinds[i].count = 0;
            g_kinds[i].distinctDst = 0;
            g_kinds[i].lastDst = nullptr;
        }
        LeaveCriticalSection(&g_lock);
        log_line("[d3d11] last %lu s: waits so far %ld (last for %llu);%s", kSummaryEveryMs / 1000, g_waits,
                 g_lastWaitValue, at ? line : " no copies");
    }
    return 0;
}
}  // namespace

void* desk_detour(void* fn, void* hook, const char* what, void** real) { return detour(fn, hook, what, real); }

// Always: watch the VR mod's device creation (shareable.cpp needs the device). watch = also log copies and waits.
void start_d3d11_probe(HMODULE vr_mod, bool watch) {
    g_vrMod = vr_mod;
    g_watch = watch;
    InitializeCriticalSection(&g_lock);
    bool ok = patch_named_import(vr_mod, "D3D11CreateDevice", &hook_create, reinterpret_cast<void**>(&g_realCreate));
    log_line("[d3d11] the VR mod's device creation is %s%s", ok ? "watched" : "NOT watched (no such import)",
             watch ? "; the copy probe is on" : "");
    if (!watch) return;
    if (HANDLE t = CreateThread(nullptr, 0, probe_thread, nullptr, 0, nullptr)) CloseHandle(t);
}
