package com.seciii.irbl.sourceCodePreprocess;

import com.github.javaparser.JavaParser;
import com.github.javaparser.ParseResult;
import com.github.javaparser.ast.CompilationUnit;

import java.io.FileOutputStream;
import java.io.IOException;
import java.io.PrintStream;
import java.nio.file.Paths;

/**
 * author: GLH
 * date:   2021-04-03
 * 该类的目的是提取每个源代码文件中的类名、方法名和变量名，并将其输出到json文件中
 */
public class ASTGenerator {
    public static void generateASTasXML(String sourceCode, String target) {
        try {
            ParseResult<CompilationUnit> result = new JavaParser().parse(Paths.get(sourceCode));
            // 输出重定向到目标文件
            PrintStream ori = System.out;
            FileOutputStream puts = new FileOutputStream(target, false);
            System.setOut(new PrintStream(puts));
            // 将结果输出到文件中
            result.getResult().ifPresent(MyXMLPrinter::print);
            // 恢复重定向
            System.setOut(ori);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
