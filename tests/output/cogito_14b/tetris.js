// ... (javascript code) ...
function rotateBlock(block) {
    const newBlocks = Array(4).fill(null).map(r=> {
        return new Array(r);
    });
    for (const [r,c] of block.entries()){
        const cc = (block[3-r][c]);