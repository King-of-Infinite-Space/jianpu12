尝试制作简谱

比较常用的（非专业级）制谱软件有图形界面的MuseScore以及使用标记语言的Lilypond。然而默认都不支持简谱。

用Lilypond生成简谱有以下两个方案：
1. [ssb22/jianpu-ly: Jianpu in Lilypond](https://github.com/ssb22/jianpu-ly)
   用自定义的简谱格式写谱，通过python脚本转换为可用Lilypond渲染的格式。
2. [nybbs2003/lilypond-Jianpu: Display plugin of Jianpu notation for Lilypond](https://github.com/nybbs2003/lilypond-Jianpu)
    用Lilypond格式写谱，引入Lilypond的拓展`jianpu10a.ly`从而渲染出简谱。（见[示例](https://github.com/nybbs2003/lilypond-Jianpu/blob/master/7-speech%2Bjianpu_10a.ly)）

后者更原生，而前者支持的样式似乎更多一些。总之两方案功能都不完善，但都能胜任简单情况。

---

因不习惯字母记谱，目前使用方案1。但想试用[12个数字的简谱](https://king-of-infinite-space.github.io/posts/202110-%E5%A5%BD%E8%84%BE%E6%B0%94%E7%9A%84%E7%90%B4%E9%94%AE.html)，所以写了脚本进行转换。还有附加功能方便自己的学习。

To do (or not to do) \
支持 `.jp12` ↔ `.ly` 的转换（从而支持方案2且能利用已有谱库）