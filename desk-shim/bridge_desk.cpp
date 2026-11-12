// bridge_desk.dll -- an xNVSE add-on of our own, loaded ONLY by the desk-test profiles ("<rung> sim").
//
// Why: with the Virtual Desktop Streamer running and nobody in the headset, Virtual Desktop's body-tracking
// memory ("VirtualDesktop.BodyState") exists but is empty. TTWVR 1.0.0 trusts it over its own body solver, so on
// a desk run the player has no body and the world is black (modding-notes/2026-11-11-why-no-3d-world-...).
// The Streamer runs with admin rights and a desk session cannot quit it.
//
// What it does: inside the game's process, the VR mod's question "is that memory there?" (the Windows call
// OpenFileMappingW, asked through TTWVR.dll's own import table) is answered "no" for that one name. Every other
// name goes to Windows unchanged. Nothing of TTWVR's is changed on disk; nothing is touched outside this process.
// Never part of a profile a person plays: in the headset the memory is real and must be read.
#include <windows.h>
#include <cstdio>
#include <cwchar>

namespace {
const wchar_t kBodyMemory[] = L"VirtualDesktop.BodyState";
const char kTargetModule[] = "TTWVR.dll";
const char kImportName[] = "OpenFileMappingW";
const DWORD kWaitForModMs = 120000;
const DWORD kPollMs = 100;

typedef HANDLE(WINAPI* OpenFileMappingW_t)(DWORD, BOOL, LPCWSTR);
OpenFileMappingW_t g_real = nullptr;
volatile LONG g_answered = 0;

void log_line(const char* fmt, ...) {
    char path[MAX_PATH];
    DWORD n = GetEnvironmentVariableA("USERPROFILE", path, MAX_PATH);
    if (!n || n > MAX_PATH - 64) return;
    strcat_s(path, "\\Documents\\My Games\\FalloutNV\\bridge_desk.log");
    FILE* f = nullptr;
    if (fopen_s(&f, path, "a") || !f) return;
    SYSTEMTIME t;
    GetLocalTime(&t);
    fprintf(f, "%02u:%02u:%02u ", t.wHour, t.wMinute, t.wSecond);
    va_list a;
    va_start(a, fmt);
    vfprintf(f, fmt, a);
    va_end(a);
    fputc('\n', f);
    fclose(f);
}

HANDLE WINAPI hook_OpenFileMappingW(DWORD access, BOOL inherit, LPCWSTR name) {
    if (name && wcsstr(name, kBodyMemory)) {
        if (InterlockedIncrement(&g_answered) == 1)
            log_line("first ask for %ls answered 'not there' (desk run)", kBodyMemory);
        SetLastError(ERROR_FILE_NOT_FOUND);
        return nullptr;
    }
    return g_real(access, inherit, name);
}

// Replace one named import in a loaded module's import table. True when it was found and replaced.
bool patch_import(HMODULE mod) {
    BYTE* base = reinterpret_cast<BYTE*>(mod);
    auto dos = reinterpret_cast<IMAGE_DOS_HEADER*>(base);
    auto nt = reinterpret_cast<IMAGE_NT_HEADERS*>(base + dos->e_lfanew);
    auto dir = nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT];
    if (!dir.VirtualAddress) return false;
    for (auto d = reinterpret_cast<IMAGE_IMPORT_DESCRIPTOR*>(base + dir.VirtualAddress); d->Name; ++d) {
        if (!d->OriginalFirstThunk) continue;
        auto names = reinterpret_cast<IMAGE_THUNK_DATA*>(base + d->OriginalFirstThunk);
        auto slots = reinterpret_cast<IMAGE_THUNK_DATA*>(base + d->FirstThunk);
        for (; names->u1.AddressOfData; ++names, ++slots) {
            if (IMAGE_SNAP_BY_ORDINAL(names->u1.Ordinal)) continue;
            auto by_name = reinterpret_cast<IMAGE_IMPORT_BY_NAME*>(base + names->u1.AddressOfData);
            if (strcmp(by_name->Name, kImportName) != 0) continue;
            DWORD old = 0;
            if (!VirtualProtect(&slots->u1.Function, sizeof(void*), PAGE_READWRITE, &old)) return false;
            g_real = reinterpret_cast<OpenFileMappingW_t>(slots->u1.Function);
            slots->u1.Function = reinterpret_cast<ULONG_PTR>(&hook_OpenFileMappingW);
            VirtualProtect(&slots->u1.Function, sizeof(void*), old, &old);
            return true;
        }
    }
    return false;
}

DWORD WINAPI wait_and_patch(LPVOID) {
    for (DWORD waited = 0; waited < kWaitForModMs; waited += kPollMs) {
        if (HMODULE mod = GetModuleHandleA(kTargetModule)) {
            bool ok = patch_import(mod);
            log_line(ok ? "%s found after %lu ms: its question about Virtual Desktop's body memory is now answered here"
                        : "%s found after %lu ms but it has no import named OpenFileMappingW: NOTHING CHANGED",
                     kTargetModule, waited);
            return 0;
        }
        Sleep(kPollMs);
    }
    log_line("%s never loaded in %lu ms: nothing changed", kTargetModule, kWaitForModMs);
    return 0;
}
}  // namespace

struct PluginInfo {
    enum { kInfoVersion = 1 };
    UINT32 infoVersion;
    const char* name;
    UINT32 version;
};

extern "C" {
__declspec(dllexport) bool NVSEPlugin_Query(const void*, PluginInfo* info) {
    info->infoVersion = PluginInfo::kInfoVersion;
    info->name = "BridgeDesk";
    info->version = 1;
    return true;
}

__declspec(dllexport) bool NVSEPlugin_Load(const void*) {
    static bool started = false;
    if (!started) {
        started = true;
        log_line("bridge_desk loaded");
        if (HANDLE t = CreateThread(nullptr, 0, wait_and_patch, nullptr, 0, nullptr)) CloseHandle(t);
    }
    return true;
}
}
