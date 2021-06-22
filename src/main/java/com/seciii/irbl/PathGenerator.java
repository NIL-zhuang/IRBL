package com.seciii.irbl;

import java.io.File;

public class PathGenerator {
    public static String generatePath(String[] tokens) {
        //        返回/*/*/*/的路径字符串
        StringBuilder path = new StringBuilder();
        for (String token : tokens) {
            path.append(token).append(File.separator);
        }
        return path.toString();
    }
}
