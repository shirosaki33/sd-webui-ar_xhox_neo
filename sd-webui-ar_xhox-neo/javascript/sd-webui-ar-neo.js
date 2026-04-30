(function () {
    "use strict";

    function app() {
        return typeof gradioApp === "function" ? gradioApp() : document;
    }

    function fireInput(el, value) {
        if (!el) return false;
        el.value = value;
        el.dispatchEvent(new Event("input", { bubbles: true }));
        el.dispatchEvent(new Event("change", { bubbles: true }));
        return true;
    }

    function findNumberInput(elemId) {
        const root = app();
        const container = root.querySelector(`#${CSS.escape(elemId)}`);
        if (!container) return null;
        if (container.matches && container.matches("input")) return container;
        return container.querySelector("input[type='number'], input");
    }

    function setWebuiSize(tab, width, height) {
        const prefix = tab === "img2img" ? "img2img" : "txt2img";
        const widthInput = findNumberInput(`${prefix}_width`);
        const heightInput = findNumberInput(`${prefix}_height`);
        const okW = fireInput(widthInput, width);
        const okH = fireInput(heightInput, height);
        return okW && okH;
    }

    function buttonData(btn) {
        const id = btn.id || "";
        const match = id.match(/^arx_btn_(txt2img|img2img)_(\d+)_(\d+)$/);
        if (!match) return null;
        return { tab: match[1], width: parseInt(match[2], 10), height: parseInt(match[3], 10) };
    }

    function bindResolutionButtons() {
        app().querySelectorAll("button[id^='arx_btn_']").forEach((btn) => {
            if (btn.dataset.arxBound === "1") return;
            const data = buttonData(btn);
            if (!data) return;
            btn.dataset.arxBound = "1";
            btn.title = btn.title || `Set ${data.width} x ${data.height}`;
            btn.addEventListener("click", (ev) => {
                setWebuiSize(data.tab, data.width, data.height);
            }, true);
        });
    }

    function getCurrentSize(tab) {
        const prefix = tab === "img2img" ? "img2img" : "txt2img";
        const w = findNumberInput(`${prefix}_width`);
        const h = findNumberInput(`${prefix}_height`);
        return [w ? w.value : 0, h ? h.value : 0];
    }

    function bindCalculatorButtons() {
        app().querySelectorAll("button[id^='arx_get_current_']").forEach((btn) => {
            if (btn.dataset.arxBound === "1") return;
            btn.dataset.arxBound = "1";
            btn.addEventListener("click", () => {
                const tab = btn.id.replace("arx_get_current_", "");
                const box = btn.closest(".gradio-accordion, .block, div");
                const nums = box ? box.querySelectorAll("input[type='number']") : [];
                const [w, h] = getCurrentSize(tab);
                if (nums[0]) fireInput(nums[0], w);
                if (nums[1]) fireInput(nums[1], h);
            }, true);
        });

        app().querySelectorAll("button[id^='arx_apply_calc_']").forEach((btn) => {
            if (btn.dataset.arxBound === "1") return;
            btn.dataset.arxBound = "1";
            btn.addEventListener("click", () => {
                const tab = btn.id.replace("arx_apply_calc_", "");
                const box = btn.closest(".gradio-accordion, .block, div");
                const nums = box ? box.querySelectorAll("input[type='number']") : [];
                const w = nums[2] ? nums[2].value : 0;
                const h = nums[3] ? nums[3].value : 0;
                if (w && h) setWebuiSize(tab, w, h);
            }, true);
        });
    }

    function bindAll() {
        bindResolutionButtons();
        bindCalculatorButtons();
    }

    if (typeof onUiLoaded === "function") onUiLoaded(bindAll);
    if (typeof onUiUpdate === "function") onUiUpdate(bindAll);
    document.addEventListener("DOMContentLoaded", bindAll);
})();
