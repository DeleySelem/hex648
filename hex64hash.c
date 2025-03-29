#include <stdint.h>

void Hex64Hash(uint32_t *ctx) {
    uint32_t eax, ebx, ecx, edx, edi;

    // First quadrant processing
    eax = ctx[0];
    ebx = ctx[1];
    ecx = ctx[2];
    edx = ctx[3];

    eax += ebx;
    ecx ^= eax;
    ecx = (ecx << 7) | (ecx >> (32 - 7));
    edx += ecx;
    ebx ^= edx;
    ebx = (ebx >> 11) | (ebx << (32 - 11));
    eax += ebx;
    ecx ^= eax;
    ecx = (ecx << 13) | (ecx >> (32 - 13));
    edx += ecx;
    ebx ^= edx;
    ebx = (ebx >> 17) | (ebx << (32 - 17));

    ctx[0] = eax;
    ctx[1] = ebx;
    ctx[2] = ecx;
    ctx[3] = edx;

    // Second quadrant processing
    eax = ctx[4];
    ebx = ctx[5];
    ecx = ctx[6];
    edx = ctx[7];

    edi = eax + ebx;
    edi ^= ecx;
    edi = (edi << 5) | (edi >> (32 - 5));
    edx += edi;
    eax ^= edx;
    ebx = __builtin_bswap32(ebx);
    ecx += ebx;
    edx ^= ecx;
    edx = (edx >> 9) | (edx << (32 - 9));

    ctx[4] = eax;
    ctx[5] = ebx;
    ctx[6] = ecx;
    ctx[7] = edx;

    // Cross-mixing
    ctx[3] ^= eax;
    ctx[7] ^= ebx;
    ctx[1] += ecx;
    ctx[5] -= edx;
}
