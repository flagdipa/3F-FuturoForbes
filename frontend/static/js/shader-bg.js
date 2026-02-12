document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('shader-canvas');
    if (!canvas) return;

    const gl = canvas.getContext('webgl');
    if (!gl) return;

    const vsSource = `
        attribute vec4 aVertexPosition;
        void main() { gl_Position = aVertexPosition; }
    `;

    const fsSource = `
        precision highp float;
        uniform vec2 iResolution;
        uniform float iTime;

        const float overallSpeed = 0.15;
        const float lineAmplitude = 0.8;
        const vec4 lineColor = vec4(0.145, 0.588, 0.745, 1.0); // Eastern Blue
        const int linesPerGroup = 12;

        float random(float t) {
            return (cos(t) + cos(t * 1.3 + 1.3) + cos(t * 1.4 + 1.4)) / 3.0;
        }

        void main() {
            vec2 uv = gl_FragCoord.xy / iResolution.xy;
            vec2 fragCoord = gl_FragCoord.xy;
            vec2 space = (fragCoord - iResolution.xy / 2.0) / iResolution.x * 2.0 * 5.0;

            float horizontalFade = 1.0 - (cos(uv.x * 6.28) * 0.5 + 0.5);
            float verticalFade = 1.0 - (cos(uv.y * 6.28) * 0.5 + 0.5);

            space.y += random(space.x * 0.5 + iTime * 0.2) * 1.0 * (0.5 + horizontalFade);
            space.x += random(space.y * 0.5 + iTime * 0.2 + 2.0) * 1.0 * horizontalFade;

            vec4 lines = vec4(0.0);
            vec4 bgColor1 = vec4(0.015, 0.058, 0.074, 1.0); // Base Dark
            vec4 bgColor2 = vec4(0.027, 0.117, 0.149, 1.0); // Lighter Dark

            for(int l = 0; l < 12; l++) {
                float floatL = float(l);
                float offsetTime = iTime * 0.25;
                float offsetPosition = floatL + space.x * 0.5;
                float rand = random(offsetPosition + offsetTime) * 0.5 + 0.5;
                float halfWidth = mix(0.01, 0.15, rand * horizontalFade) / 2.0;
                float offset = random(offsetPosition + offsetTime * (1.1 + floatL/12.0)) * mix(0.6, 2.0, horizontalFade);
                
                float linePos = random(space.x * 0.2 + iTime * 0.2) * horizontalFade * lineAmplitude + offset;
                float dist = abs(linePos - space.y);
                float lineEffect = smoothstep(halfWidth, 0.0, dist) / 2.0 + smoothstep(halfWidth * 0.15, 0.0, dist);
                
                lines += lineEffect * lineColor * rand;
            }

            gl_FragColor = mix(bgColor1, bgColor2, uv.y) * verticalFade + lines;
            gl_FragColor.a = 1.0;
        }
    `;

    function initShader() {
        const vs = gl.createShader(gl.VERTEX_SHADER);
        gl.shaderSource(vs, vsSource);
        gl.compileShader(vs);
        const fs = gl.createShader(gl.FRAGMENT_SHADER);
        gl.shaderSource(fs, fsSource);
        gl.compileShader(fs);
        const prog = gl.createProgram();
        gl.attachShader(prog, vs);
        gl.attachShader(prog, fs);
        gl.linkProgram(prog);
        return prog;
    }

    const program = initShader();
    const posLoc = gl.getAttribLocation(program, 'aVertexPosition');
    const resLoc = gl.getUniformLocation(program, 'iResolution');
    const timeLoc = gl.getUniformLocation(program, 'iTime');

    const buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);

    function render(time) {
        // Handle window resize or canvas not matching display size
        const displayWidth = canvas.clientWidth;
        const displayHeight = canvas.clientHeight;

        if (canvas.width !== displayWidth ||
            canvas.height !== displayHeight) {
            canvas.width = displayWidth;
            canvas.height = displayHeight;
        }

        gl.viewport(0, 0, canvas.width, canvas.height);
        gl.useProgram(program);
        gl.uniform2f(resLoc, canvas.width, canvas.height);
        gl.uniform1f(timeLoc, time * 0.001);
        gl.enableVertexAttribArray(posLoc);
        gl.vertexAttribPointer(posLoc, 2, gl.FLOAT, false, 0, 0);
        gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
        requestAnimationFrame(render);
    }
    requestAnimationFrame(render);
});
