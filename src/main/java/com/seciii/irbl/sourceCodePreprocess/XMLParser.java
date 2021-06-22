package com.seciii.irbl.sourceCodePreprocess;

import org.w3c.dom.Document;
import org.w3c.dom.NodeList;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import java.io.File;
import java.io.FileOutputStream;
import java.io.PrintStream;

public class XMLParser {
    /**
     * 从xml文档中提取出有用的注释信息，输出到文件中
     * @param source xml源文件
     * @param target 输出的目标文件
     */
    public void extractComment(String source, String target) {
        try {
            File in = new File(source);
            File out = new File(target);
            PrintStream ps = new PrintStream(new FileOutputStream(out));
            DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
            DocumentBuilder builder = factory.newDocumentBuilder();
            Document doc = builder.parse(in);

            NodeList nl = doc.getElementsByTagName("comment");
            for (int i = 1; i < nl.getLength(); i++) {
//                System.out.println(nl.item(i).getAttributes().getNamedItem("content").getNodeValue());
//                System.out.println("-----------------------------------------------------");
                ps.println(nl.item(i).getAttributes().getNamedItem("content").getNodeValue().trim());
            }
        } catch (Exception e) {
            System.out.println(source);
            e.printStackTrace();
            // do nothing
        }
    }
}
