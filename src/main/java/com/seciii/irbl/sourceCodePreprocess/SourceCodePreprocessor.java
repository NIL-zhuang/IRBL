package com.seciii.irbl.sourceCodePreprocess;

import java.io.*;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

import com.seciii.irbl.util.ProgressBar;
import com.seciii.irbl.PathGenerator;

/**
 * author: glh
 * data:   2021-04-07
 * 该类用来进行源代码的处理，提取处源代码中的类名、方法名、变量名及注释
 */
public class SourceCodePreprocessor {
    public void generateXML(String sourcePath, String xmlPath, String commentPath) {
        XMLParser xmlParser = new XMLParser();
        ASTGenerator.generateASTasXML(sourcePath,xmlPath);
        xmlParser.extractComment(xmlPath, commentPath);
    }

    public void generateJSON(String sourcePath, String targetPath) {
        SourceCodeInfoExtractor sourceCodeInfoExtractor = new SourceCodeInfoExtractor();
        sourceCodeInfoExtractor.extractMainInfo(sourcePath, targetPath);
    }

    public static void main(String[] args) {
        String dataset = "eclipse";
        String rootPath = "data" + File.separator + dataset + File.separator;

        // 提取文件列表
        String fileIndex = rootPath + "fileIndex.csv";
        File file = new File(fileIndex);
        Map<Integer, String> allFiles = new TreeMap<>();
        try {
            BufferedReader reader = new BufferedReader(new FileReader(file));
            String line;
            while ((line = reader.readLine()) != null) {
                String[] lst = line.split(",");
                allFiles.put(Integer.parseInt(lst[0]),lst[1]);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }

        // 创建两个文件夹
        File dir = new File(rootPath + "json");
        dir.mkdir();
        dir = new File(rootPath + "xml");
        dir.mkdir();
        dir = new File(rootPath + "comment");
        dir.mkdir();

        // 开始逐个文件处理
        ProgressBar progressBar = new ProgressBar(allFiles.size());
        progressBar.init("预处理文件: ");
        SourceCodePreprocessor scp = new SourceCodePreprocessor();
        for (int i = 0; i < allFiles.size(); i++) {
            if (!allFiles.get(i).endsWith(".java"))
                continue;

            progressBar.printProgress(i+1);
            String sourcePath = rootPath + "src" + File.separator + allFiles.get(i);
            String jsonFilepath = rootPath + "json" + File.separator + String.valueOf(i) + ".json";
            String xmlFilepath = rootPath + "xml" + File.separator + String.valueOf(i) + ".xml";
            String commentFilepath = rootPath + "comment" + File.separator + String.valueOf(i) + ".txt";

            scp.generateXML(sourcePath, xmlFilepath, commentFilepath);
            scp.generateJSON(sourcePath, jsonFilepath);
        }
        System.out.println("\n预处理成功！");

    }
}
