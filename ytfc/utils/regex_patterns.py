import re


username_pattern = r'^@[\.a-zA-Z0-9_-]{3,30}$'
USERNAME_PATTERN = re.compile(username_pattern)

channel_pattern = '^(UC|UU|FL|UULF|UULV|UUSH|UULP|UUPV|UUPS|UUMO|UUMF|UUMV|UUMS)[a-zA-Z0-9_-]{22}$'
CHANNEL_PATTERN = re.compile(channel_pattern)

regular_list_pattern = '^(PL[a-zA-Z0-9_-]{16}|PL[a-zA-Z0-9_-]{32})$'
PL_PATTERN = re.compile(regular_list_pattern)

mix_pattern = '^RD[a-zA-Z0-9_-]{11,}$'
RD_PATTERN = re.compile(mix_pattern)

music_list_pattern = '^OLAK5uy_[klmn]{1}[A-Za-z0-9_-]{32}$'
OL_PATTERN = re.compile(music_list_pattern)
