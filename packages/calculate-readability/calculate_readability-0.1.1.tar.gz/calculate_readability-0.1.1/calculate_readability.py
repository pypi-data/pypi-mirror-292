import re
import math
from divide_char_type import divide_char_type
from count_syllable import count_syllable

def jfre(sentence, sentence_type):
    asl_sum = len(sentence)
    asw_sum = 0
    for i in range(len(sentence_type)):
        # 単語がアルファベットの場合
        if sentence_type[i] == 3:
            asw_sum += count_syllable(sentence[i])
        # 単語が漢字の場合
        elif sentence_type[i] == 2:
            asw_sum += len(sentence[i])
        # 単語がその他記号など以外の場合
        elif sentence_type[i] != 5:
            asw_sum += 1

        # 単語がその他記号などの場合
        if sentence_type[i] == 5:
            asl_sum -= 1
    asl = asl_sum
    asw = asw_sum/asl_sum
    result = 206.835-(1.015*asl)-(84.6*asw) 
    return result


def jfkg(sentence, sentence_type):
    asl_sum = len(sentence)
    asw_sum = 0
    for i in range(len(sentence_type)):
        # 単語がアルファベットの場合
        if sentence_type[i] == 3:
            asw_sum += count_syllable(sentence[i])
        # 単語が漢字の場合
        elif sentence_type[i] == 2:
            asw_sum += len(sentence[i])
        # 単語がその他記号など以外の場合
        elif sentence_type[i] != 5:
            asw_sum += 1

        # 単語がその他記号などの場合
        if sentence_type[i] == 5:
            asl_sum -= 1
    asl = asl_sum
    asw = asw_sum/asl_sum
    result = (0.39*asl)+(11.8*asw)-15.59 
    return result


def jari(sentence, sentence_type):
    asl_sum = len(sentence)
    acw_sum = 0
    for i in range(len(sentence_type)):
        # 単語が平仮名の場合
        if sentence_type[i] == 0:
            acw_sum += math.log(1/88)/math.log(1/61)*len(sentence[i])
        # 単語がカタカナの場合
        elif sentence_type[i] == 1:
            acw_sum += math.log(1/141)/math.log(1/61)*len(sentence[i])
        # 単語が漢字の場合
        elif sentence_type[i] == 2:
            acw_sum += math.log(1/20898)/math.log(1/61)*len(sentence[i])
        # 単語がアルファベット,数字の場合
        if sentence_type[i] == 3 or sentence_type[i] == 4:
            acw_sum += len(sentence[i])
        # 単語がその他記号などの場合
        elif sentence_type[i] == 5:
            asl_sum -= 1
    asl = asl_sum
    acw = acw_sum/asl_sum
    result = (4.71*acw)+(0.5*asl)-21.43 
    return result


def jcli(sentence, sentence_type):
    asl_sum = len(sentence)
    acw_sum = 0
    for i in range(len(sentence_type)):
        # 単語が平仮名の場合
        if sentence_type[i] == 0:
            acw_sum += math.log(1/88)/math.log(1/61)*len(sentence[i])
        # 単語がカタカナの場合
        elif sentence_type[i] == 1:
            acw_sum += math.log(1/141)/math.log(1/61)*len(sentence[i])
        # 単語が漢字の場合
        elif sentence_type[i] == 2:
            acw_sum += math.log(1/20898)/math.log(1/61)*len(sentence[i])
        # 単語がアルファベット,数字の場合
        if sentence_type[i] == 3 or sentence_type[i] == 4:
            acw_sum += len(sentence[i])
        # 単語がその他記号などの場合
        elif sentence_type[i] == 5:
            asl_sum -= 1
    asl = asl_sum
    acw = acw_sum/asl_sum
    result = (5.88*acw)+(29.6/asl)-15.8 
    return result


def jsmog(sentence, sentence_type):
    ps = 0
    for i in range(len(sentence_type)):
        # 単語がアルファベットの場合
        if sentence_type[i] == 3:
            if count_syllable(sentence[i]) >= 3:
                ps += 1
        # 単語が漢字の場合
        elif sentence_type[i] == 2:
            if len(sentence[i]) >= 3:
                ps += 1
    result = 1.031*math.sqrt(30*ps)+3.1291
    return result


def calculate_readability(document):
    re_break = re.compile("\r?\n")          # 段落の正規表現
    re_point = re.compile("[.．…。!?！？]") # 句点の正規表現

    # URLの置換
    re_url = re.compile(r"https?://[-0-9a-zA-Z+&@#/%?=~\.\_]+")
    text = re.sub(re_url, "url", document)

    # mailの置換
    re_mail = re.compile(r"[^@]+@[^@]+")
    text = re.sub(re_mail, "mail", text)

    text = re.sub("\r?\n\r?\n*", "\n", text)     # 複数改行を削除 
    text = re.sub("\r?\n$", "", text)            # 文末の改行を削除
    text_break = re.split(re_break, text)        # 段落単位に分割

    fixed_text = divide_char_type(text)[0]       # 整形後字種分割リスト
    data = {"raw_text":document, "text":fixed_text, "jfre":None, "jfkg":None, "jari":None, "jcli":None, "jsmog":None,
            "break":[]
           }

    # 全体のリーダビリティ計算
    all_jfre = 0
    all_jfkg = 0
    all_jari = 0
    all_jcli = 0
    all_jsmog = 0

    # 段落単位で解析
    for b in text_break:
        divide_break = divide_char_type(b)      # 字種分割
        len_divide_break = len(divide_break[0]) # 字種分割語数

        # 段落のリーダビリティ計算
        break_jfre = 0
        break_jfkg = 0
        break_jari = 0
        break_jcli = 0
        break_jsmog = 0

        sentence_list = [] # センテンス一覧
        sentence = []      # 各センテンスの単語一覧
        sentence_type = [] # 各センテンスの単語の文字種一覧

        # 字種分割語単位で解析
        for i in range(len_divide_break):
            sentence.append(divide_break[0][i])
            sentence_type.append(divide_break[1][i])

            # 字種分割結果がその他記号などの場合
            if divide_break[1][i] == 5:
                # 句点判定がマッチした場合
                if re.search(re_point, divide_break[0][i]):
                    # センテンスのリーダビリティ計算
                    sentence_jfre = jfre(sentence, sentence_type)
                    sentence_jfkg = jfkg(sentence, sentence_type)
                    sentence_jari = jari(sentence, sentence_type)
                    sentence_jcli = jcli(sentence, sentence_type)
                    sentence_jsmog = jsmog(sentence, sentence_type)

                    # センテンスの情報格納
                    sentence_list.append({"text":sentence,
                                          "jfre":sentence_jfre,
                                          "jfkg":sentence_jfkg,
                                          "jari":sentence_jari,
                                          "jcli":sentence_jcli,
                                          "jsmog":sentence_jsmog
                                         })

                    # 段落のリーダビリティ計算
                    break_jfre += sentence_jfre
                    break_jfkg += sentence_jfkg
                    break_jari += sentence_jari
                    break_jcli += sentence_jcli
                    break_jsmog += sentence_jsmog

                    # センテンス分割に伴う初期化
                    sentence = []
                    sentence_type = []
        # 文末においてセンテンスが空でない場合
        if sentence != []:
            # センテンスのリーダビリティ計算
            sentence_jfre = jfre(sentence, sentence_type)
            sentence_jfkg = jfkg(sentence, sentence_type)
            sentence_jari = jari(sentence, sentence_type)
            sentence_jcli = jcli(sentence, sentence_type)
            sentence_jsmog = jsmog(sentence, sentence_type)

            # センテンスの情報格納
            sentence_list.append({"text":sentence,
                                  "jfre":sentence_jfre,
                                  "jfkg":sentence_jfkg,
                                  "jari":sentence_jari,
                                  "jcli":sentence_jcli,
                                  "jsmog":sentence_jsmog
                                 })

            # 段落のリーダビリティ計算
            break_jfre += sentence_jfre
            break_jfkg += sentence_jfkg
            break_jari += sentence_jari
            break_jcli += sentence_jcli
            break_jsmog += sentence_jsmog

        # 段落の情報格納
        data["break"].append({})
        data["break"][-1]["text"] = divide_break[0]
        data["break"][-1]["jfre"] = break_jfre/len(sentence_list)
        data["break"][-1]["jfkg"] = break_jfkg/len(sentence_list)
        data["break"][-1]["jari"] = break_jari/len(sentence_list)
        data["break"][-1]["jcli"] = break_jcli/len(sentence_list)
        data["break"][-1]["jsmog"] = break_jsmog/len(sentence_list)
        data["break"][-1]["sentence"] = sentence_list

        # 全体のリーダビリティ計算
        all_jfre += data["break"][-1]["jfre"]
        all_jfkg += data["break"][-1]["jfkg"]
        all_jari += data["break"][-1]["jari"]
        all_jcli += data["break"][-1]["jcli"]
        all_jsmog += data["break"][-1]["jsmog"]

    # 全体の情報格納
    data["jfre"] = all_jfre/len(text_break)
    data["jfkg"] = all_jfkg/len(text_break)
    data["jari"] = all_jari/len(text_break)
    data["jcli"] = all_jcli/len(text_break)
    data["jsmog"] = all_jsmog/len(text_break)

    return data
