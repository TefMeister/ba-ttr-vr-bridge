// shareable.cpp -- desk runs only: the pretend headset's eye pictures are made the shareable kind.
//
// Why (found 2026-11-12 with d3d11_probe.cpp): with its upscaler on, TTWVR 1.0.0 has its helper program
// (ttwvr_dlss_host.exe) write each finished eye straight into the HEADSET's own picture, through a handle another
// program can open. Virtual Desktop's pictures can be opened that way. The OpenXR Simulator's are plain pictures
// (no sharing flags), so the helper never writes one (it reports "none" for every frame), the mod's own output
// pictures are 16x16 stand-ins, and the mod's last resort copies the previous headset picture forward: a frozen eye.
//
// What it does: when a picture of the simulator's swapchain shape is made on the game's Direct3D 11
// device, the same picture is made with the sharing flags added. Nothing else about it changes, and no
// other caller's pictures are touched. If Direct3D refuses the flags, the picture is made exactly as asked.
// BRIDGE_DESK_SHAREABLE in the environment: 0 = off; a hex number = other flags to try (default 2).
#include <windows.h>
#include <d3d11.h>
#include <intrin.h>
#include <cstdlib>
#include <cstring>

void log_line(const char* fmt, ...);
void* desk_detour(void* fn, void* hook, const char* what, void** real);

namespace {
const int kSlotCreateTexture2D = 5;                // ID3D11Device::CreateTexture2D in the device's method table
// The OLD kind of sharing (0x2), on purpose: the mod asks each headset picture for its handle the old way
// (IDXGIResource::GetSharedHandle), which the newer kind (0x802) refuses. Tried live 2026-11-12: 0x802 frozen, 0x2 live.
const UINT kDefaultFlags = D3D11_RESOURCE_MISC_SHARED;
const UINT kSmallestEye = 256;                     // smaller pictures are not eyes or panels
const LONG kLogFirst = 16;

typedef HRESULT(STDMETHODCALLTYPE* CreateTexture2D_t)(ID3D11Device*, const D3D11_TEXTURE2D_DESC*,
                                                      const D3D11_SUBRESOURCE_DATA*, ID3D11Texture2D**);
CreateTexture2D_t g_real = nullptr;
UINT g_flags = kDefaultFlags;
LONG g_made = 0, g_refused = 0;
bool g_hooked = false;
bool g_tell = false;                               // BRIDGE_DESK_D3D11_PROBE=1: also say what every large picture request looks like
LONG g_told = 0;
const LONG kTellFirst = 40;

// The simulator's swapchain pictures, by their shape: a colour picture without a fixed colour reading ("typeless"),
// usable both to draw into and to read from, and with no flags. TTWVR's own pictures all have a fixed format or
// carry sharing flags already. (Who asks cannot be used: every request arrives through TTWVR.dll.)
bool simulator_swapchain_shape(const D3D11_TEXTURE2D_DESC& d) {
    const bool typeless = d.Format == DXGI_FORMAT_B8G8R8A8_TYPELESS || d.Format == DXGI_FORMAT_R8G8B8A8_TYPELESS ||
                          d.Format == DXGI_FORMAT_R16G16B16A16_TYPELESS || d.Format == DXGI_FORMAT_R10G10B10A2_TYPELESS;
    return typeless && d.MiscFlags == 0 && d.Usage == D3D11_USAGE_DEFAULT &&
           d.BindFlags == (D3D11_BIND_RENDER_TARGET | D3D11_BIND_SHADER_RESOURCE) && d.SampleDesc.Count == 1 &&
           d.ArraySize == 1 && d.MipLevels == 1 && d.Width >= kSmallestEye;
}

HRESULT STDMETHODCALLTYPE hook_create_texture(ID3D11Device* dev, const D3D11_TEXTURE2D_DESC* desc,
                                              const D3D11_SUBRESOURCE_DATA* data, ID3D11Texture2D** out) {
    if (g_tell && desc && desc->Width >= kSmallestEye && InterlockedIncrement(&g_told) <= kTellFirst) {
        HMODULE owner = nullptr;
        char name[MAX_PATH] = "?";
        if (GetModuleHandleExA(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS | GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
                               static_cast<LPCSTR>(_ReturnAddress()), &owner) && owner)
            GetModuleFileNameA(owner, name, MAX_PATH);
        const char* leaf = strrchr(name, '\\');
        log_line("[shareable] seen: %ux%u format %u usage %u bind 0x%X misc 0x%X mips %u array %u samples %u data %d out %d, asked by %s",
                 desc->Width, desc->Height, desc->Format, desc->Usage, desc->BindFlags, desc->MiscFlags, desc->MipLevels,
                 desc->ArraySize, desc->SampleDesc.Count, data != nullptr, out != nullptr, leaf ? leaf + 1 : name);
    }
    if (desc && out && !data && simulator_swapchain_shape(*desc)) {
        D3D11_TEXTURE2D_DESC shared = *desc;
        shared.MiscFlags = g_flags;
        HRESULT hr = g_real(dev, &shared, data, out);
        if (SUCCEEDED(hr)) {
            if (InterlockedIncrement(&g_made) <= kLogFirst)
                log_line("[shareable] the simulator's %ux%u picture (format %u) made shareable (flags 0x%X)", desc->Width,
                         desc->Height, desc->Format, g_flags);
            return hr;
        }
        if (InterlockedIncrement(&g_refused) <= kLogFirst)
            log_line("[shareable] Direct3D refused the sharing flags for a %ux%u picture (format %u): 0x%08lX - made as asked",
                     desc->Width, desc->Height, desc->Format, hr);
    }
    return g_real(dev, desc, data, out);
}
}  // namespace

// Called for every Direct3D 11 device the VR mod makes; the routine is shared, so it is hooked once.
void shareable_on_device(ID3D11Device* dev) {
    if (!dev || g_hooked) return;
    char v[16] = {};
    if (GetEnvironmentVariableA("BRIDGE_DESK_SHAREABLE", v, sizeof(v))) {
        g_flags = static_cast<UINT>(strtoul(v, nullptr, 16));
        if (!g_flags) {
            log_line("[shareable] switched off by BRIDGE_DESK_SHAREABLE=0");
            g_hooked = true;
            return;
        }
    }
    g_hooked = true;
    char probe[4] = {};
    g_tell = GetEnvironmentVariableA("BRIDGE_DESK_D3D11_PROBE", probe, sizeof(probe)) && probe[0] == '1';
    void* fn = (*reinterpret_cast<void***>(dev))[kSlotCreateTexture2D];
    desk_detour(fn, &hook_create_texture, "CreateTexture2D", reinterpret_cast<void**>(&g_real));
    log_line("[shareable] the simulator's eye pictures will be made shareable (flags 0x%X): %s", g_flags,
             g_real ? "on" : "COULD NOT BE SET UP");
}
