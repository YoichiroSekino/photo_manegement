<?xml version="1.0" encoding="Shift_JIS"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="html" encoding="Shift_JIS" indent="yes"/>

<xsl:template match="/">
<html>
<head>
<title>デジタル写真管理情報</title>
<style type="text/css">
body { font-family: "MS Gothic", monospace; font-size: 12px; }
table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
th, td { border: 1px solid #000; padding: 5px; text-align: left; }
th { background-color: #e0e0e0; }
.header { background-color: #4472C4; color: white; padding: 10px; }
.photo-info { margin-bottom: 30px; }
</style>
</head>
<body>
<div class="header">
<h1>デジタル写真管理情報</h1>
<p>DTD Version: <xsl:value-of select="/photodata/@DTD_version"/></p>
</div>

<h2>基礎情報</h2>
<table>
<tr><th>項目</th><th>内容</th></tr>
<tr>
<td>写真フォルダ名</td>
<td><xsl:value-of select="/photodata/基礎情報/写真フォルダ名"/></td>
</tr>
<tr>
<td>適用要領基準</td>
<td><xsl:value-of select="/photodata/基礎情報/適用要領基準"/></td>
</tr>
<xsl:if test="/photodata/基礎情報/工事件名">
<tr>
<td>工事件名</td>
<td><xsl:value-of select="/photodata/基礎情報/工事件名"/></td>
</tr>
</xsl:if>
<xsl:if test="/photodata/基礎情報/工事番号">
<tr>
<td>工事番号</td>
<td><xsl:value-of select="/photodata/基礎情報/工事番号"/></td>
</tr>
</xsl:if>
</table>

<h2>写真情報</h2>
<xsl:for-each select="/photodata/写真情報">
<div class="photo-info">
<h3>写真 <xsl:value-of select="position()"/></h3>

<table>
<tr><th>項目</th><th>内容</th></tr>
<tr>
<td>シリアル番号</td>
<td><xsl:value-of select="写真ファイル情報/シリアル番号"/></td>
</tr>
<tr>
<td>写真ファイル名</td>
<td><xsl:value-of select="写真ファイル情報/写真ファイル名"/></td>
</tr>
<xsl:if test="撮影工種区分/工種">
<tr>
<td>工種</td>
<td><xsl:value-of select="撮影工種区分/工種"/></td>
</tr>
</xsl:if>
<xsl:if test="撮影工種区分/種別">
<tr>
<td>種別</td>
<td><xsl:value-of select="撮影工種区分/種別"/></td>
</tr>
</xsl:if>
<xsl:if test="撮影工種区分/細別">
<tr>
<td>細別</td>
<td><xsl:value-of select="撮影工種区分/細別"/></td>
</tr>
</xsl:if>
<tr>
<td>写真タイトル</td>
<td><xsl:value-of select="撮影情報/写真タイトル"/></td>
</tr>
<xsl:if test="撮影情報/撮影年月日">
<tr>
<td>撮影年月日</td>
<td><xsl:value-of select="撮影情報/撮影年月日"/></td>
</tr>
</xsl:if>
<xsl:if test="撮影情報/写真区分">
<tr>
<td>写真区分</td>
<td><xsl:value-of select="撮影情報/写真区分"/></td>
</tr>
</xsl:if>
<xsl:if test="撮影情報/測点">
<tr>
<td>測点</td>
<td><xsl:value-of select="撮影情報/測点"/></td>
</tr>
</xsl:if>
<xsl:if test="撮影情報/設計寸法">
<tr>
<td>設計寸法</td>
<td><xsl:value-of select="撮影情報/設計寸法"/></td>
</tr>
</xsl:if>
<xsl:if test="撮影情報/実測寸法">
<tr>
<td>実測寸法</td>
<td><xsl:value-of select="撮影情報/実測寸法"/></td>
</tr>
</xsl:if>
<xsl:if test="撮影情報/検査員">
<tr>
<td>検査員</td>
<td><xsl:value-of select="撮影情報/検査員"/></td>
</tr>
</xsl:if>
</table>
</div>
</xsl:for-each>

</body>
</html>
</xsl:template>

</xsl:stylesheet>
