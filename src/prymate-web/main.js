import { FitAddon } from "@xterm/addon-fit";
import { WebglAddon } from "@xterm/addon-webgl";
import { Terminal } from "@xterm/xterm";

import "@xterm/xterm/css/xterm.css";

import PyodideWorker from "./python.worker.js?worker";

class PyodideTerminal {
    constructor() {
        this.xterm = new Terminal({
            convertEol: true,
            fontFamily: "monospace",
            fontSize: 18,
            theme: {
                background: "#1d1d20",
            },
        });

        this.fitAddon = new FitAddon();
        this.webglAddon = new WebglAddon();

        this.inputBuffer = "";
        this.resolveInput = null;

        this.xterm.onData((data) => this.onData(data));
    }

    open(container) {
        this.xterm.open(container);

        this.xterm.loadAddon(this.fitAddon);
        this.xterm.loadAddon(this.webglAddon);

        this.fitAddon.fit();
        window.addEventListener("resize", () => this.fitAddon.fit());
    }

    // TODO: handle key up and key down
    onData(data) {
        for (let i = 0; i < data.length; i++) {
            const c = data[i];

            // CR/LF
            if (c === "\r" || c === "\n") {
                this.xterm.write("\n"); // carriage return automatically added by xterm.js

                // resolve waiting promise (if any)
                if (this.resolveInput) {
                    this.resolveInput(this.inputBuffer + "\n");
                    this.resolveInput = null;
                }

                this.inputBuffer = "";
                continue;
            }

            // Backspace / DEL
            if (c === "\u007f" || c === "\b") {
                if (this.inputBuffer.length > 0) {
                    this.inputBuffer = this.inputBuffer.slice(0, -1);
                    this.xterm.write("\b \b");
                }
            }

            // Ctrl + C
            if (c === "\u0003") {
                this.xterm.write("^C\n");

                if (this.resolveInput) {
                    this.resolveInput("");
                    this.resolveInput = null;
                }

                this.inputBuffer = "";
                continue;
            }

            // printable character
            this.inputBuffer += c;
            this.xterm.write(c);
        }
    }

    write(charCode) {
        this.xterm.write(String.fromCharCode(charCode));
    }

    async read(bufferChrView, bufferIntView) {
        const inputValue = await new Promise((resolve) => {
            this.resolveInput = resolve;
        });

        const encodedBytes = new TextEncoder().encode(inputValue);
        const maxBytes = (bufferIntView.length - 1) * Int32Array.BYTES_PER_ELEMENT;

        if (encodedBytes.length > maxBytes) {
            console.warn("truncating input, too long for shared buffer");
        }

        const chrWritten = Math.min(encodedBytes.length, maxBytes);

        for (let i = 0; i < chrWritten; i++) {
            bufferChrView[i + Int32Array.BYTES_PER_ELEMENT] = encodedBytes[i];
        }

        bufferIntView[0] = chrWritten;
        Atomics.notify(bufferIntView, 0, 1);
    }
}

async function main() {
    const pyodideWorker = new PyodideWorker();
    const terminal = new PyodideTerminal();

    terminal.open(document.getElementById("terminal-container"));

    pyodideWorker.onmessage = (event) => {
        switch (event.data.type) {
            case "stdout":
                terminal.write(event.data.stdout);
                break;

            case "stderr":
                terminal.write(event.data.stderr);
                break;

            case "stdin":
                const bufferChrView = new Uint8Array(event.data.buffer);
                const bufferIntView = new Int32Array(event.data.buffer);

                terminal.read(bufferChrView, bufferIntView);
                break;

            case "finished":
                console.log("program finished execution");
                break;

            default:
                console.warn(`unknown worker message ${event.data.type}`);
                break;
        }
    };

    pyodideWorker.postMessage({
        type: "run",
    });
}

main();
