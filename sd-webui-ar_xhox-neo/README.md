# sd-webui-ar_xhox Neo patch

Neo-compatible lightweight version of `xhoxye/sd-webui-ar_xhox`.

## What changed

- Avoids direct dependency on `modules.ui_components.ToolButton` by falling back to `gr.Button`.
- Does not rely on `after_component` to capture width/height components.
- Uses JavaScript to set `txt2img_width`, `txt2img_height`, `img2img_width`, and `img2img_height` by DOM id.
- Keeps `SD15_resolutions.txt`, `SDXL_resolutions.txt`, and `Custom_resolutions.txt` support.

## Install

Put this folder in:

```text
sd-webui-forge-neo/extensions/sd-webui-ar_xhox-neo
```

Restart Neo.

Custom resolutions are stored in:

```text
sd-webui-ar_xhox-neo/Custom_resolutions.txt
```

Format:

```text
1024*1024 # optional comment
832*1216
1216*832
```
