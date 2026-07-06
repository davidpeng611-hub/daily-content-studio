set downloadFolder to (POSIX path of (path to downloads folder)) & "YT下载"
set ytdlpPath to (POSIX path of (path to home folder)) & "bin/yt-dlp"
set ffmpegPath to (POSIX path of (path to home folder)) & "bin/ffmpeg"

display dialog "粘贴整段分享文案或视频链接：" default answer "" buttons {"取消", "开始下载"} default button "开始下载" cancel button "取消" with title "YT下载器"
set pastedText to text returned of result
set videoURL to do shell script "/usr/bin/python3 -c " & quoted form of "import re, sys
text = sys.stdin.read()
match = re.search(r'https?://[^\\s，。！!]+', text)
print(match.group(0) if match else '')" & " <<< " & quoted form of pastedText

if videoURL is "" then
	display dialog "没有找到视频链接。" buttons {"好"} default button "好" with title "YT下载器"
	return
end if

do shell script "mkdir -p " & quoted form of downloadFolder

try
	do shell script quoted form of ytdlpPath & " --ffmpeg-location " & quoted form of ffmpegPath & " -P " & quoted form of downloadFolder & " -o '%(title).180B [%(id)s].%(ext)s' " & quoted form of videoURL
	display notification "下载完成，已保存到“下载/YT下载”。" with title "YT下载器"
	display dialog "下载完成！文件已保存到“下载/YT下载”。" buttons {"打开文件夹", "好"} default button "好" with title "YT下载器"
	if button returned of result is "打开文件夹" then
		do shell script "open " & quoted form of downloadFolder
	end if
on error errorMessage
	display dialog "下载失败：" & return & errorMessage buttons {"好"} default button "好" with title "YT下载器"
end try
