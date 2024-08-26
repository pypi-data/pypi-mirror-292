IF "shou1".DONE THEN
    FOR #i := 0 TO 61 DO
        IF "a语音".r_data[#i] = ',' OR "a语音".r_data[#i] = 0 OR "a语音".r_data[#i] = ';' THEN
            Chars_TO_Strg(Chars := "a语音".r_data,
                          pChars := #i_1,
                          Cnt := #i - #i_1,
                          Strg => "a语音".u_data[#i_2]);
            #i_1 := #i + 1;
            #i_2 += 1;
        END_IF;
    END_FOR;
    "a语音".r_data := "a语音".e_data;
    IF "a语音".u_data[0] = 'yy_plc_ewm' THEN
        "发送"(buf := 'qewm08',
             num := 4);
        "发送"(buf := 'qewm08',
             num := 1);
    END_IF;
    IF "a语音".u_data[0] = 'yy_plc_sz' THEN
        "发送"(buf := 'qsz_02',
             num := 4);
        "发送"(buf := 'qsz_02',
             num := 1);
    END_IF;
    IF "a语音".u_data[0] = 'yy_plc_kb' THEN
        "发送"(buf := 'qkb_01',
             num := 4);
        "发送"(buf := 'qkb_01',
             num := 1);
    END_IF;
    IF "a语音".u_data[0] = 'yy_plc_ry' THEN
        "发送"(buf := 'qry_03',
             num := 4);
        "发送"(buf := 'qry_03',
             num := 1);
    END_IF; 
END_IF;
---------------------
IF "shou2".DONE THEN
    FOR #i := 0 TO 61 DO
        IF "b图像".r_data[#i] = ',' OR "b图像".r_data[#i] = 0 OR "b图像".r_data[#i] = ';' THEN
            Chars_TO_Strg(Chars := "b图像".r_data,
                          pChars := #i_1,
                          Cnt := #i - #i_1,
                          Strg => "b图像".u_data[#i_2]);
            #i_1 := #i + 1;
            #i_2 += 1;
        END_IF;
    END_FOR;
    "b图像".r_data := "b图像".e_data;

    IF "b图像".u_data[0]='tx_plc_wz' THEN
        FOR #i := 2 TO 3 DO
            IF "b图像".u_data[1] = "c视觉".r1[#i] THEN
                "发送"(buf := 'fwz_15',
                     num := 4);
            ELSIF "b图像".u_data[1] ="c视觉".r2[#i] THEN
                "发送"(buf := 'fwz_16',
                     num := 4);
            ELSIF "b图像".u_data[1] = "c视觉".r3[#i] THEN
                "发送"(buf := 'fwz_17',
                     num := 4);
            ELSIF "b图像".u_data[1] = "c视觉".r4[#i] THEN
                "发送"(buf := 'fwz_18',
                     num := 4);
            ELSE
                "发送"(buf := 'fwz_23',
                     num := 4);
            END_IF;
        END_FOR;
    END_IF;

END_IF;
-------------------------------------
IF "shou3".DONE THEN
    FOR #i := 0 TO 61 DO
        IF "c视觉".r_data[#i] = ',' OR "c视觉".r_data[#i] = 0 OR "c视觉".r_data[#i] = ';' THEN
            Chars_TO_Strg(Chars := "c视觉".r_data,
                          pChars := #i_1,
                          Cnt := #i - #i_1,
                          Strg => "c视觉".u_data[#i_2]);
            #i_1 := #i + 1;
            #i_2 += 1;
        END_IF;
    END_FOR;
    "c视觉".r_data := "c视觉".e_data;
    IF "c视觉".u_data[0] = 'sj_plc_ewm' THEN
        IF "c视觉".u_data[1] = 'low' THEN
            "发送"(buf := 'fewm15',
                 num := 4);
            "a语音".xh[1] := 1;

        END_IF;
        IF "c视觉".u_data[1] = 'mid' THEN
            "发送"(buf := 'fewm16',
                 num := 4);
            "a语音".xh[2] := 1;

        END_IF;
        IF "c视觉".u_data[1] = 'high' THEN
            "发送"(buf := 'fewm17',
                 num := 4);
            "a语音".xh[3] := 1;
        END_IF;
    ELSIF "c视觉".u_data[0] = 'sj_plc_sz' THEN
        IF "c视觉".u_data[1] = '1' THEN
            "发送"(buf := 'fsz_18',
                 num := 4);
            "a语音".xh[11] := 1;
        END_IF;
        IF "c视觉".u_data[1] = '2' THEN
            "发送"(buf := 'fsz_18',
                 num := 1);
            "a语音".xh[12] := 1;
        END_IF;
        IF "c视觉".u_data[1] = '3' THEN
            "发送"(buf := 'fsz_18',
                 num := 4);
            "a语音".xh[13] := 1;
        END_IF;
        "发送"(buf := 'plc_yy_ok',
             num := 1);
    ELSIF "c视觉".u_data[0] = 'sj_plc_ry' THEN
        IF "c视觉".u_data[2] = '2018' THEN
            "发送"(buf := 'fry_15',
                 num := 4);
            "c视觉".u_data[2] := '6';
        ELSIF "c视觉".u_data[2] = '2008' THEN
            "发送"(buf := 'fry_16',
                 num := 4);
            "c视觉".u_data[2] := '16';
        ELSIF "c视觉".u_data[2] = '1998' THEN
            "发送"(buf := 'fry_17',
                 num := 4);
            "c视觉".u_data[2] := '26';
        ELSIF "c视觉".u_data[2] = '1988' THEN
            "发送"(buf := 'fry_18',
                 num := 4);
            "c视觉".u_data[2] := '36';
        END_IF;
        FOR #i := 0 TO 4 DO
            IF "renyuan_jishu"=0THEN
                "c视觉".r1[#i] := "c视觉".u_data[#i + 1];
            ELSIF "renyuan_jishu"=1 THEN
                "c视觉".r2[#i] := "c视觉".u_data[#i + 1];
            ELSIF "renyuan_jishu"=2 THEN
                "c视觉".r3[#i] := "c视觉".u_data[#i + 1];
            ELSIF "renyuan_jishu"=3 THEN
                "c视觉".r4[#i] := "c视觉".u_data[#i + 1];
            END_IF;
        END_FOR;
    ELSIF "c视觉".u_data[0]='sj_plc_wz_ok' THEN
        "发送"(buf := 'plc_tx_wz',
             num := 2);
    END_IF;
END_IF;


———————————————————————
IF "shou4".DONE THEN
    FOR #i := 0 TO 61 DO
        IF "d机器人".r_data[#i] = ',' OR "d机器人".r_data[#i] = 0 OR "d机器人".r_data[#i] = ';' THEN
            Chars_TO_Strg(Chars := "d机器人".r_data,
                          pChars := #i_1,
                          Cnt := #i - #i_1,
                          Strg => "d机器人".u_data[#i_2]);
            #i_1 := #i + 1;
            #i_2 += 1;
        END_IF;
    END_FOR;
    "d机器人".r_data := "d机器人".e_data;
    IF "d机器人".u_data[0] = 'jqr_plc_ewm' THEN
        "发送"(buf := 'plc_sj_ewm',
             num := 3);
    ELSIF "d机器人".u_data[0] = 'jqr_plc_ewm_again' THEN
        "ewm_jishu" += 1;
        IF "ewm_jishu" < 3 THEN
            IF "ewm_jishu" = 1 THEN
                "发送"(buf := 'qewm10',
                     num := 4);
            END_IF;
            IF "ewm_jishu" = 2 THEN
                "发送"(buf := 'qewm12',
                     num := 4);
            END_IF;
        ELSE
            "ewm_jishu" := 0;
            "发送"(buf := 'plc_yy_ok',
                 num := 1);
        END_IF;
    ELSIF "d机器人".u_data[0] = 'jqr_plc_sz' THEN
        "发送"(buf := 'plc_sj_sz',
             num := 3);
    ELSIF "d机器人".u_data[0] = 'jqr_plc_ry' THEN
        "发送"(buf := 'plc_sj_ry',
             num := 3);
    ELSIF "d机器人".u_data[0] = 'jqr_plc_ry_again' THEN
        "renyuan_jishu" += 1;
        IF "renyuan_jishu" < 4 THEN
            IF "renyuan_jishu" = 1 THEN
                "发送"(buf := 'qry_04',
                     num := 4);
            END_IF;
            IF "renyuan_jishu" = 2 THEN
                "发送"(buf := 'qry_05',
                     num := 4);
            END_IF;
            IF "renyuan_jishu" = 3 THEN
                "发送"(buf := 'qry_06',
                     num := 4);
            END_IF;
        ELSE
            "renyuan_jishu" := 0;
            "发送"(buf := 'plc_yy_ok',
                 num := 1);
        END_IF;
    ELSIF "d机器人".u_data[0] = 'jqr_plc_kb' THEN
        IF "i0.1" THEN
            "发送"(buf := 'fkb_23',
                 num := 4);
            "a语音".xh[21] := 1;
        ELSIF "i0.2" THEN
            "发送"(buf := 'fkb_23',
                 num := 4);
            "a语音".xh[22] := 1;
        ELSIF "i0.3" THEN
            "发送"(buf := 'fkb_23',
                 num := 4);
            "a语音".xh[23] := 1;
        ELSIF "i1.4" THEN
            "发送"(buf := 'fkb_23',
                 num := 4);
            "a语音".xh[23] := 1;
        ELSE
            "发送"(buf := 'fkb_23',
                 num := 4);
            "a语音".xh[24] := 1;
        END_IF;
        "发送"(buf := 'plc_yy_ok',
             num := 1);
    END_IF;
    ELSIF"d机器人".u_data[0]='jqr_plc_wz_again' THEN
        IF "物资检测" AND "到位检测" = 0 THEN
            "传送带" := 3;
        END_IF;
END_IF;

——————————————————————
IF "shou5".DONE THEN
    FOR #i := 0 TO 61 DO
        IF "e按钮".r_data[#i] = ',' OR "e按钮".r_data[#i] = 0 OR "e按钮".r_data[#i] = ';' THEN
            Chars_TO_Strg(Chars := "e按钮".r_data,
                          pChars := #i_1,
                          Cnt := #i - #i_1,
                          Strg => "e按钮".u_data[#i_2]);
            #i_1 := #i + 1;
            #i_2 += 1;
        END_IF;
    END_FOR;
    IF "e按钮".u_data[0] = 'an_plc_zz' THEN
        "传送带" := 1;
    ELSIF "e按钮".u_data[0] = 'an_plc_fz' THEN
        "传送带" := 2;
    ELSIF "e按钮".u_data[0] = 'an_plc_wz' THEN
        IF "物资检测" AND "到位检测" = 0 THEN
            "传送带" := 3;
        END_IF;
    END_IF;
    "e按钮".r_data := "e按钮".e_data;
    "a语音".u_data[0]:='0';
END_IF;
——————————————————————
"发送长度" := LEN(#buf);
IF #num = 2 THEN
    Strg_TO_Chars(Strg := #buf,
                  pChars := 0,
                  Cnt => #len,
                  Chars := "b图像".s_data);
    "发送标志" := 1;
END_IF;
IF #num = 3 THEN
    Strg_TO_Chars(Strg := #buf,
                  pChars := 0,
                  Cnt => #len,
                  Chars := "c视觉".s_data);
    "发送标志" := 1;
END_IF;
IF #num = 4 THEN
    Strg_TO_Chars(Strg := #buf,
                  pChars := 0,
                  Cnt => #len,
                  Chars := "d机器人".s_data);
    "发送标志" := 1;
END_IF;
IF #num = 1 THEN
    Strg_TO_Chars(Strg := #buf,
                  pChars := 0,
                  Cnt => #len,
                  Chars := "a语音".s_data);
    "发送标志" := 1;
END_IF;
IF #num = 5 THEN
    Strg_TO_Chars(Strg := #buf,
                  pChars := 0,
                  Cnt => #len,
                  Chars := "e按钮".s_data);
    "发送标志" := 1;
END_IF;
