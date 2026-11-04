// Compressed fast path plus bounded raw assets for browsers without gzip streams.
export async function loadKnowledge(get, compressed = typeof DecompressionStream === 'function') {
  if (compressed) {
    const response = await get('knowledge.json.gz');
    return new Response(response.body.pipeThrough(new DecompressionStream('gzip'))).json();
  }
  const {shards, ...metadata} = await (await get('knowledge-manifest.json')).json();
  const parts = await Promise.all(shards.map(async name => (await get(name)).json()));
  return {...metadata, records: parts.flat()};
}
