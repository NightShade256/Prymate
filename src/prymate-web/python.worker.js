import { loadPyodide } from "pyodide";

/* need the integer view solely for Atomics.wait and Atomics.notify */
const sharedBuf = new SharedArrayBuffer(Int32Array.BYTES_PER_ELEMENT * 256);
const bufferChrView = new Uint8Array(sharedBuf);
const bufferIntView = new Int32Array(sharedBuf);

async function setupPyodide() {
    const pyodide = await loadPyodide({
        indexURL: "/pyodide",
        packages: ["/prymate-0.6.0-py3-none-any.whl"],
    });

    pyodide.setStdin({
        isatty: true,
        stdin: () => {
            /* main thread stores number of characters (bytes) read at index zero */
            Atomics.store(bufferIntView, 0, -1);
            postMessage({ type: "stdin", buffer: sharedBuf });
            Atomics.wait(bufferIntView, 0, -1);

            return new TextDecoder("utf8").decode(
                bufferChrView.slice(
                    Int32Array.BYTES_PER_ELEMENT,
                    Int32Array.BYTES_PER_ELEMENT + Atomics.load(bufferIntView, 0)
                )
            );
        },
    });

    pyodide.setStdout({
        isatty: true,
        raw: (charCode) => {
            postMessage({
                type: "stdout",
                stdout: charCode,
            });
        },
    });

    pyodide.setStderr({
        isatty: true,
        raw: (charCode) => {
            postMessage({
                type: "stderr",
                stderr: charCode,
            });
        },
    });

    return pyodide;
}

onmessage = async (event) => {
    switch (event.data.type) {
        case "run":
            const pyodide = await setupPyodide();

            const prymate = pyodide.pyimport("prymate");
            prymate.main();

            /* TODO: return the actual return code */
            postMessage({
                type: "finished",
                returnCode: 0,
            });

            break;

        default:
            console.warn(`unknown main thread message ${event.data.type}`);
            break;
    }
};
