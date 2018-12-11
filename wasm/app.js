const { readFileSync } = require('fs');

function red(text) {
    return '\x1b[0m\x1b[31m' + text + '\x1b[0m';
}

function green(text) {
    return '\x1b[0m\x1b[32m' + text + '\x1b[0m';
}

function yellow(text) {
    return '\x1b[0m\x1b[33m' + text + '\x1b[0m';
}

function stringDecoder(mem) {
    return function(addr) {
        const i8 = new Int8Array(mem.buffer);
        const start = addr;
        var s = "";
        while (i8[addr] != 0) {
            s += String.fromCharCode(i8[addr++]);
        }
        return s;
    }
}

function evaluate(mem, policy, input) {

    console.log(yellow("-> Initializing Wasm address space."));
    const str = JSON.stringify(input)
    const addr = policy.instance.exports.opa_malloc(str.length);
    const buf = new Uint8Array(mem.buffer);

    for(let i = 0; i < str.length; i++) {
        buf[addr+i] = str.charCodeAt(i);
    }

    console.log(yellow("-> Evaluating policy."));
    const returnCode = policy.instance.exports.eval(addr, str.length);

    return {returnCode: returnCode};
}

async function main() {

    const mem = new WebAssembly.Memory({initial: 5});
    const addr2string = stringDecoder(mem);

    console.log(yellow("-> Loading Wasm policy from disk."));
    const policy = await WebAssembly.instantiate(readFileSync('policy.wasm'), {
        env: {
            memory: mem,
            opa_abort: function(addr) {
                throw addr2string(addr);
            },
        },
    });

    const result = evaluate(mem, policy, JSON.parse(process.argv[2]));

    if (result.returnCode != 1) {
        console.log(red("Decision: DENY"));
    } else {
        console.log(green("Decision: ALLOW"));
    }
}

main();
