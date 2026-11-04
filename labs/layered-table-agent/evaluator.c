/* Integer-only evaluation of a validated topologically ordered Boolean DAG.
 * Model buffers are supplied by the JS loader; no host imports or I/O.
 */
typedef unsigned int u32;
typedef unsigned char u8;
__attribute__((export_name("evaluate")))
int evaluate(u8 *bits, u32 inputs, const u32 *nodes, u32 count,
             const u32 *votes, u32 vote_count, const int *bias,
             int *scores, u32 classes) {
    if (inputs > 65536 || count > 1000000 || classes > 1024) return -1;
    for (u32 i = 0; i < inputs; ++i) if (bits[i] > 1) return -2;
    for (u32 i = 0; i < count; ++i) {
        u32 a=nodes[3*i], b=nodes[3*i+1], f=nodes[3*i+2];
        if (a >= inputs+i || b >= inputs+i || f > 15) return -3;
        bits[inputs+i]=(f >> (3-2*bits[a]-bits[b])) & 1;
    }
    for (u32 c=0;c<classes;++c) scores[c]=bias[c];
    for (u32 v=0;v<vote_count;++v) {
        u32 signal=votes[3*v], polarity=votes[3*v+1], c=votes[3*v+2];
        if (signal>=inputs+count || polarity>1 || c>=classes) return -4;
        scores[c] += bits[signal] ^ polarity;
    }
    return 0;
}
