
> 注：当前项目为 Serverless Devs 应用，由于应用中会存在需要初始化才可运行的变量（例如应用部署地区、函数名等等），所以**不推荐**直接 Clone 本仓库到本地进行部署或直接复制 s.yaml 使用，**强烈推荐**通过 `s init ${模版名称}` 的方法或应用中心进行初始化，详情可参考[部署 & 体验](#部署--体验) 。

# fc-comfyui 帮助文档
<p align="center" class="flex justify-center">
    <a href="https://www.serverless-devs.com" class="ml-1">
    <img src="http://editor.devsapp.cn/icon?package=fc-comfyui&type=packageType">
  </a>
  <a href="http://www.devsapp.cn/details.html?name=fc-comfyui" class="ml-1">
    <img src="http://editor.devsapp.cn/icon?package=fc-comfyui&type=packageVersion">
  </a>
  <a href="http://www.devsapp.cn/details.html?name=fc-comfyui" class="ml-1">
    <img src="http://editor.devsapp.cn/icon?package=fc-comfyui&type=packageDownload">
  </a>
</p>

<description>

部署 ComfyUI 到阿里云函数计算

</description>

<codeUrl>



</codeUrl>
<preview>



</preview>


## 前期准备

使用该项目，您需要有开通以下服务并拥有对应权限：

<service>
</service>

<remark>



</remark>

<disclaimers>



</disclaimers>

## 部署 & 体验

<appcenter>
   
- :fire: 通过 [Serverless 应用中心](https://fcnext.console.aliyun.com/applications/create?template=fc-comfyui) ，
  [![Deploy with Severless Devs](https://img.alicdn.com/imgextra/i1/O1CN01w5RFbX1v45s8TIXPz_!!6000000006118-55-tps-95-28.svg)](https://fcnext.console.aliyun.com/applications/create?template=fc-comfyui) 该应用。
   
</appcenter>
<deploy>
    
- 通过 [Serverless Devs Cli](https://www.serverless-devs.com/serverless-devs/install) 进行部署：
  - [安装 Serverless Devs Cli 开发者工具](https://www.serverless-devs.com/serverless-devs/install) ，并进行[授权信息配置](https://docs.serverless-devs.com/fc/config) ；
  - 初始化项目：`s init fc-comfyui -d fc-comfyui`
  - 进入项目，并进行项目部署：`cd fc-comfyui && s deploy -y`
   
</deploy>

## 案例介绍

<appdetail id="flushContent">

本案例将 ComfyUI  部署至阿里云函数计算，实现云上进行文生图、图生图等 AIGC 创作。

ComfyUI 是一个专为 Stable Diffusion 的模型设计强大而模块化的 GUI，用户能够以节点为基础构建 AIGC 创作工作流。对于希望摆脱传统编码方式并采用更直观工作流程的用户来说，ComfyUI 是一个理想的工具。ComfyUI 由 Comfyanonymous 于 2023 年 1 月创建，开发初衷是为了学习 Stable Diffusion 模型的工作原理。由于其使用的便捷 Stable Diffusion 的创建者 Stability AI 也使用 ComfyUI 进行内部测试，并聘请了 Comfyanonymous 来帮助他们开发内部工具 。目前 ComfyUI 在 Github 上有超过 3 千 Fork，并且拥有超过 3 万 Star。

Stable Diffusion 是一款开源的扩散模型，由 CompVis、Stability AI 和 LAION 的研究人员和工程师创建。由于 Stable Diffusion 开源、扩展性强的特点，其受到了全球众多 AIGC 爱好者的追捧。根据模型网站 Civital 统计，目前最热门的模型已经超过 100 万次下载，超过 10 万次下载的模型 70 余个，各种风格、不同功能的模型超过 12 万。

ComfyUI 在国内也很火热，通过 ComfyUI 进行文生图的教程在国内各大平台多次登入热搜榜、排行榜，引领了一波又一波的浪潮。

</appdetail>

## 使用流程

<usedetail id="flushContent">

### 基本文生图

进入页面后，点击 Queue Prompt 开始运行工作流，稍等片刻后即可得到第一张图片

![](https://img.alicdn.com/imgextra/i2/O1CN01nML52f1mIRwjP3sPy_!!6000000004931-0-tps-1226-889.jpg)

您可以随时使用 “Load Default” 恢复默认的工作流，请自行保存已经编辑好的工作流，避免丢失。

<div id="mount_nas" />

### 挂载 NAS 使用自定义节点和模型


默认创建的 ComfyUI 不支持上传自己的模型以及第三方节点，要上传文件首先需要绑定文件管理 NAS

通过应用详情，跳转到函数控制台
![](https://img.alicdn.com/imgextra/i2/O1CN01LQQyBF1jPN5LrmrYj_!!6000000004540-0-tps-1078-985.jpg)

在函数详情，进行网络配置，绑定 专有网络/交换机。
如果您当前没有相关资源，可以点击 “创建新的 VPC”、“创建新的交换机”，前往相关产品创建资源。专有网络、交换机不计费
![](https://img.alicdn.com/imgextra/i4/O1CN01OPYefo1LCxZaaN2P7_!!6000000001264-0-tps-1359-897.jpg)


网络配置完毕后，进行 NAS 挂载配置。绑定对应专有网络、交换机下存在的 NAS 挂载点
函数本地目录请填写 `/mnt/auto` 或 `/mnt/auto/comfyui`

如果您当前没有相关资源，可以点击 “创建新的 NAS 文件系统”，并在 NAS 控制台创建 专有网络/交换机 下的挂载点。
需要注意，大模型对文件 IO 要求较高，建议创建 **通用性能型 NAS 实例**。NAS 会根据存储的文件大小进行计费，不通规格的 NAS 计费单价不一致，请参考相关文档。

如果您曾经在当前 NAS 中使用过 Stable Diffusion 应用，可以考虑将远端目录设置为 `/fc-stable-diffusion-plus`，本地目录设置为 `/mnt/auto`

![](https://img.alicdn.com/imgextra/i3/O1CN01JM4qq427roSToC5GI_!!6000000007851-0-tps-1424-1061.jpg)

挂载完毕后，关闭所有 ComfyUI 静置几分钟（如果之前未开启 ComfyUI 页面可跳过），访问 ComfyUI 地址，等待进入页面。
首次挂载 NAS 需要进行文件链接操作，这可能会花费几分钟时间，如果页面加载失败可以刷新一次（挂载耗时太久导致启动超时，通常重试一次即可）

### 进入终端、上传文件

函数计算支持登入运行中的函数实例
![](https://img.alicdn.com/imgextra/i2/O1CN01p2zERS21sNFaFIFlK_!!6000000007040-0-tps-1522-846.jpg)

您可以在终端中执行需要的操作（如手动安装自定义节点、依赖等）

注意，在 Serverless 环境下，您的所有改动都不会真正保存，您需要将改动的文件放置在 NAS 中以持久化

如果您希望上传本地的模型文件，可以使用 NAS 文件浏览器功能

![](https://img.alicdn.com/imgextra/i1/O1CN01qBoRgE1Us1czB7Doi_!!6000000002572-0-tps-1533-574.jpg)


### 安装自定义节点

以安装中文翻译 [AIGODLIKE-COMFYUI-TRANSLATION](https://github.com/AIGODLIKE/AIGODLIKE-COMFYUI-TRANSLATION) 为例

首先 [挂载 NAS 并使用自定义节点和模型](#mount_nas)

使用 ComfyUI-Manager 进行安装，
![](https://img.alicdn.com/imgextra/i1/O1CN01cpHWUJ1WQfCKAZoVB_!!6000000002783-0-tps-1339-893.jpg)

搜索要安装的节点名称，点击 install
![](https://img.alicdn.com/imgextra/i2/O1CN014lNLJe1lebUP6PYxn_!!6000000004844-0-tps-1368-270.jpg)

**注意**
- 安装过程中请不要关闭页面。安装完成后，除去需要点击 restart 外，还需要刷新页面
- 安装过程中可能会访问 Github、HuggingFace 等境外网站，由于网络问题可能会导致访问较慢或失败，您可以在网络上检索如何解决类似的问题。 )

安装完成后，在设置修改语言即可
![](https://img.alicdn.com/imgextra/i3/O1CN017lGKCE22e0RIZb8UN_!!6000000007144-0-tps-1193-1014.jpg)

翻译插件提供的中文仅供参考，为了避免在与其他人交流时存在偏差，建议在交流关键信息时使用原本的英文单词

### 使用国内 pypi 镜像，加速依赖下载

首先，登陆进入实例或进入文件管理器
在 `/mnt/auto/comfyui/root/.pip/pip.conf`

```
[global]
index-url = http://mirrors.aliyun.com/pypi/simple/
[install]
trusted-host = https://mirrors.aliyun.com
```


### 使用别人提供的工作流时，安装缺失的节点

网络上的工作流往往使用了大量自定义节点，展现在页面上就是满屏红色的报错，这时我们需要根据需要安装缺失的第三方节点

![](https://img.alicdn.com/imgextra/i4/O1CN015Ovmyr1VPSXWcUvit_!!6000000002645-0-tps-840-442.jpg)


ComfyUI 管理器插件，可以一键安装缺失的 custom nodes
![](https://img.alicdn.com/imgextra/i2/O1CN01aSPkBh22XatVsvQrX_!!6000000007130-0-tps-1363-886.jpg)

**注意**
- 安装过程中请不要关闭页面。安装完成后，除去需要点击 restart 外，还需要刷新页面
- 安装过程中可能会访问 Github、HuggingFace 等境外网站，由于网络问题可能会导致访问较慢或失败，您可以在网络上检索如何解决类似的问题。 )


### 为什么安装了一些缺失节点仍然报错？

可以参考相关的讨论 https://comfyui-guides.runcomfy.com/ultimate-comfyui-how-tos-a-runcomfy-guide/how-to-fix-a-red-node-for-ipadapterapply

> How to fix: A red node for “IPAdapterApply”?
> You must already follow our instructions on how to install IP-Adapter V2, and it should all working properly. Now you see a red node for “IPAdapterApply”.
>
> That is because you are working on a workflow with IPAdapter V1 node, simply just replace the V1 node with the V2 ones or uninstall IPA v2 and rollback to V1 if you feel like it.


### 与 ControlNet 结合

同样的文生图，直接输出和结合 ControlNet 输出对比

![](https://img.alicdn.com/imgextra/i4/O1CN01R8bT461O1STVjkkfy_!!6000000001645-0-tps-2090-1062.jpg)

工作流如下，请自行下载需要的模型

```json
{
  "last_node_id": 29,
  "last_link_id": 54,
  "nodes": [
    {
      "id": 16,
      "type": "ControlNetLoader",
      "pos": [ 264.88020036191443, 1201.535094958983 ],
      "size": [ 376.46875, 118.875 ],
      "flags": {},
      "order": 0,
      "mode": 0,
      "outputs": [ { "name": "CONTROL_NET", "type": "CONTROL_NET", "links": [ 35 ], "shape": 3, "label": "ControlNet", "slot_index": 0 } ],
      "properties": { "Node name for S&R": "ControlNetLoader" },
      "widgets_values": [ "control_v11p_sd15_lineart.pth" ]
    },
    {
      "id": 23,
      "type": "ControlNetApplyAdvanced",
      "pos": [ 856.880200361914, 1308.535094958983 ],
      "size": { "0": 315, "1": 166 },
      "flags": {},
      "order": 6,
      "mode": 0,
      "inputs": [
        { "name": "positive", "type": "CONDITIONING", "link": 39, "label": "正面条件" },
        { "name": "negative", "type": "CONDITIONING", "link": 40, "label": "负面条件" },
        { "name": "control_net", "type": "CONTROL_NET", "link": 35, "label": "ControlNet" },
        { "name": "image", "type": "IMAGE", "link": 36, "label": "图像" }
      ],
      "outputs": [
        { "name": "positive", "type": "CONDITIONING", "links": [ 41 ], "shape": 3, "label": "正面条件", "slot_index": 0 },
        { "name": "negative", "type": "CONDITIONING", "links": [ 42 ], "shape": 3, "label": "负面条件", "slot_index": 1 }
      ],
      "properties": { "Node name for S&R": "ControlNetApplyAdvanced" },
      "widgets_values": [ 1, 0, 1 ]
    },
    {
      "id": 7,
      "type": "CLIPTextEncode",
      "pos": [ 305.4482288105471, 733.0172076020683 ],
      "size": { "0": 425.27801513671875, "1": 180.6060791015625 },
      "flags": {},
      "order": 5,
      "mode": 0,
      "inputs": [ { "name": "clip", "type": "CLIP", "link": 5, "label": "CLIP" } ],
      "outputs": [ { "name": "CONDITIONING", "type": "CONDITIONING", "links": [ 40, 45 ], "slot_index": 0, "label": "条件" } ],
      "properties": { "Node name for S&R": "CLIPTextEncode" },
      "widgets_values": [ "nsfw" ]
    },
    {
      "id": 3,
      "type": "KSampler",
      "pos": [ 1815.3138964843754, 1041.130867919922 ],
      "size": { "0": 315, "1": 262 },
      "flags": {},
      "order": 8,
      "mode": 0,
      "inputs": [
        { "name": "model", "type": "MODEL", "link": 1, "label": "模型" },
        { "name": "positive", "type": "CONDITIONING", "link": 41, "label": "正面条件" },
        { "name": "negative", "type": "CONDITIONING", "link": 42, "label": "负面条件" },
        { "name": "latent_image", "type": "LATENT", "link": 32, "label": "Latent", "slot_index": 3 }
      ],
      "outputs": [ { "name": "LATENT", "type": "LATENT", "links": [ 16 ], "slot_index": 0, "label": "Latent" } ],
      "properties": { "Node name for S&R": "KSampler" },
      "widgets_values": [ 516902852614178, "randomize", 20, 8, "euler", "normal", 1 ]
    },
    {
      "id": 8,
      "type": "VAEDecode",
      "pos": [ 2211.3138964843743, 1091.130867919922 ],
      "size": { "0": 210, "1": 46 },
      "flags": {},
      "order": 10,
      "mode": 0,
      "inputs": [
        { "name": "samples", "type": "LATENT", "link": 16, "label": "Latent" },
        { "name": "vae", "type": "VAE", "link": 43, "label": "VAE" }
      ],
      "outputs": [ { "name": "IMAGE", "type": "IMAGE", "links": [ 9 ], "slot_index": 0, "label": "图像" } ],
      "properties": { "Node name for S&R": "VAEDecode" }
    },
    {
      "id": 25,
      "type": "VAEDecode",
      "pos": [ 2285.340647460937, 637.991402648926 ],
      "size": { "0": 210, "1": 46 },
      "flags": {},
      "order": 9,
      "mode": 0,
      "inputs": [
        { "name": "samples", "type": "LATENT", "link": 48, "label": "Latent" },
        { "name": "vae", "type": "VAE", "link": 50, "label": "VAE" }
      ],
      "outputs": [ { "name": "IMAGE", "type": "IMAGE", "links": [ 49 ], "shape": 3, "label": "图像", "slot_index": 0 } ],
      "properties": { "Node name for S&R": "VAEDecode" }
    },
    {
      "id": 26,
      "type": "SaveImage",
      "pos": [ 2566.3138964843743, 631.130867919922 ],
      "size": [ 315, 270.00002098083496 ],
      "flags": {},
      "order": 11,
      "mode": 0,
      "inputs": [ { "name": "images", "type": "IMAGE", "link": 49, "label": "图像" } ],
      "properties": {},
      "widgets_values": [ "ComfyUI" ]
    },
    {
      "id": 9,
      "type": "SaveImage",
      "pos": [ 2626.3138964843743, 1022.1308679199219 ],
      "size": [ 210, 270.00002002716064 ],
      "flags": {},
      "order": 12,
      "mode": 0,
      "inputs": [ { "name": "images", "type": "IMAGE", "link": 9, "label": "图像" } ],
      "properties": {},
      "widgets_values": [ "ComfyUI" ] },
    {
      "id": 6,
      "type": "CLIPTextEncode",
      "pos": [ 304.118812936719, 462.9874991923831 ],
      "size": { "0": 422.84503173828125, "1": 164.31304931640625 },
      "flags": {},
      "order": 4,
      "mode": 0,
      "inputs": [ { "name": "clip", "type": "CLIP", "link": 3, "label": "CLIP" } ],
      "outputs": [ { "name": "CONDITIONING", "type": "CONDITIONING", "links": [ 39, 44 ], "slot_index": 0, "label": "条件" } ],
      "properties": { "Node name for S&R": "CLIPTextEncode" },
      "widgets_values": [ "1 girl" ]
    },
    {
      "id": 24,
      "type": "KSampler",
      "pos": [ 1880.3138964843754, 601.130867919922 ],
      "size": { "0": 315, "1": 262 },
      "flags": {},
      "order": 7,
      "mode": 0,
      "inputs": [
        { "name": "model", "type": "MODEL", "link": 46, "label": "模型" },
        { "name": "positive", "type": "CONDITIONING", "link": 44, "label": "正面条件" },
        { "name": "negative", "type": "CONDITIONING", "link": 45, "label": "负面条件" },
        { "name": "latent_image", "type": "LATENT", "link": 54, "label": "Latent", "slot_index": 3 }
      ],
      "outputs": [ { "name": "LATENT", "type": "LATENT", "links": [ 48 ], "shape": 3, "label": "Latent", "slot_index": 0 } ],
      "properties": { "Node name for S&R": "KSampler" },
      "widgets_values": [ 963578161132850, "randomize", 20, 8, "euler", "normal", 1 ]
    },
    {
      "id": 5,
      "type": "EmptyLatentImage",
      "pos": [ 1412.3138964843754, 744.130867919922 ],
      "size": { "0": 315, "1": 106 },
      "flags": {},
      "order": 1,
      "mode": 0,
      "outputs": [ { "name": "LATENT", "type": "LATENT", "links": [ 32, 54 ], "slot_index": 0, "label": "Latent" } ],
      "properties": { "Node name for S&R": "EmptyLatentImage" },
      "widgets_values": [ 512, 512, 1 ]
    },
    {
      "id": 12,
      "type": "LoadImage",
      "pos": [ 273.88020036191443, 1411.535094958983 ],
      "size": { "0": 315, "1": 314 },
      "flags": {},
      "order": 2,
      "mode": 0,
      "outputs": [
        { "name": "IMAGE", "type": "IMAGE", "links": [ 36 ], "shape": 3, "label": "图像", "slot_index": 0 },
        { "name": "MASK", "type": "MASK", "links": null, "shape": 3, "label": "遮罩" }
      ],
      "properties": { "Node name for S&R": "LoadImage" },
      "widgets_values": [ "example.png", "image" ]
    },
    {
      "id": 4,
      "type": "CheckpointLoaderSimple",
      "pos": [ -315.8811870632813, 556.9874991923831 ],
      "size": { "0": 356.0684509277344, "1": 159.5682373046875 },
      "flags": {},
      "order": 3,
      "mode": 0,
      "outputs": [
        { "name": "MODEL", "type": "MODEL", "links": [ 1, 46 ], "slot_index": 0, "label": "模型" },
        { "name": "CLIP", "type": "CLIP", "links": [ 3, 5 ], "slot_index": 1, "label": "CLIP" },
        { "name": "VAE", "type": "VAE", "links": [ 43, 50 ], "slot_index": 2, "label": "VAE" }
      ],
      "properties": { "Node name for S&R": "CheckpointLoaderSimple" },
      "widgets_values": [ "AWPortraitv1.1.safetensors" ]
    }
  ],
  "links": [
    [ 1, 4, 0, 3, 0, "MODEL" ],
    [ 3, 4, 1, 6, 0, "CLIP" ],
    [ 5, 4, 1, 7, 0, "CLIP" ],
    [ 9, 8, 0, 9, 0, "IMAGE" ],
    [ 16, 3, 0, 8, 0, "LATENT" ],
    [ 32, 5, 0, 3, 3, "LATENT" ],
    [ 35, 16, 0, 23, 2, "CONTROL_NET" ],
    [ 36, 12, 0, 23, 3, "IMAGE" ],
    [ 39, 6, 0, 23, 0, "CONDITIONING" ],
    [ 40, 7, 0, 23, 1, "CONDITIONING" ],
    [ 41, 23, 0, 3, 1, "CONDITIONING" ],
    [ 42, 23, 1, 3, 2, "CONDITIONING" ],
    [ 43, 4, 2, 8, 1, "VAE" ],
    [ 44, 6, 0, 24, 1, "CONDITIONING" ],
    [ 45, 7, 0, 24, 2, "CONDITIONING" ],
    [ 46, 4, 0, 24, 0, "MODEL" ],
    [ 48, 24, 0, 25, 0, "LATENT" ],
    [ 49, 25, 0, 26, 0, "IMAGE" ],
    [ 50, 4, 2, 25, 1, "VAE" ],
    [ 54, 5, 0, 24, 3, "LATENT" ]
  ],
  "groups": [
    { "title": "ControlNet", "bounding": [ 210, 1105, 1012, 660 ], "color": "#3f789e", "font_size": 24 },
    { "title": "文生图", "bounding": [ -347, 228, 1185, 747 ], "color": "#3f789e", "font_size": 24 },
    { "title": "输出", "bounding": [ 1296, 400, 1615, 951 ], "color": "#3f789e", "font_size": 24 }
  ],
  "config": {},
  "extra": {},
  "version": 0.4
}
```

</usedetail>

## 注意事项

<matters id="flushContent">

fc-comfyui（后简称“本工具”）旨在帮助用户将 ComfyUI 开源项目部署至阿里云函数计算服务。本工具为独立开发的第三方工具，与 ComfyUI 项目以及阿里云官方无直接关联。
本工具可能链接到第三方网站或服务，这些链接仅为方便用户而提供。工具开发者对这些第三方网站或服务的内容、隐私政策或操作不承担任何责任，且不表示对这些网站或服务的认可。
- ComfyUI 为开源社区较为活跃，更新频繁且功能丰富，本工具在部署时会尽量保持与社区代码一致，请自行鉴别社区代码的可靠性与稳定性；
- 在阿里云运行 ComfyUI 会产生一定的费用，请参考相关产品的计费文档；
- fc-comfyui 会帮您将 ComfyUI 部署至 函数计算 FC，如果您需要对文件（模型、第三方节点）进行持久化存储，还需要开通 文件管理 NAS，这可能会产生额外的费用；
- ComfyUI 项目的使用受其开源许可协议的约束。在使用本工具之前，请确保你已经阅读并理解了 ComfyUI 项目的许可协议，以及任何相关的第三方库或工具的许可协议；
- 将 ComfyUI 项目部署至阿里云函数计算服务，需遵守阿里云的服务条款和使用政策。请在使用本工具之前，确保你已经了解并同意阿里云的相关条款；
- 本工具按“现状”提供，不提供任何形式的明示或暗示担保，包括但不限于适销性、特定用途的适用性和不侵权的担保；
- 用户明确同意使用本工具所承担的全部风险。开发者不承担因使用或无法使用本工具所引起的任何直接、间接、偶然、特殊或后果性的损害责任；
- ComfyUI 打开页面会建立长连接请求，也即会 <span style="color:red">**持续消耗计算资源**</span>，为了避免不必要的费用产生，不使用时请 **关闭所有页面**


使用本工具即表示你理解并同意本免责声明的条款。如果你不同意本免责声明的任何部分，请不要使用本工具。

</matters>


<devgroup>


## 开发者社区

您如果有关于错误的反馈或者未来的期待，您可以在 [Serverless Devs repo Issues](https://github.com/serverless-devs/serverless-devs/issues) 中进行反馈和交流。如果您想要加入我们的讨论组或者了解 FC 组件的最新动态，您可以通过以下渠道进行：

<p align="center">  

| <img src="https://serverless-article-picture.oss-cn-hangzhou.aliyuncs.com/1635407298906_20211028074819117230.png" width="130px" > | <img src="https://serverless-article-picture.oss-cn-hangzhou.aliyuncs.com/1635407044136_20211028074404326599.png" width="130px" > | <img src="https://serverless-article-picture.oss-cn-hangzhou.aliyuncs.com/1635407252200_20211028074732517533.png" width="130px" > |
| --------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| <center>微信公众号：`serverless`</center>                                                                                         | <center>微信小助手：`xiaojiangwh`</center>                                                                                        | <center>钉钉交流群：`33947367`</center>                                                                                           |
</p>
</devgroup>
