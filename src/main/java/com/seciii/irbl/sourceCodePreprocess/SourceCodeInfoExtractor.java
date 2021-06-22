package com.seciii.irbl.sourceCodePreprocess;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import com.alibaba.fastjson.serializer.SerializerFeature;
import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.ImportDeclaration;
import com.github.javaparser.ast.PackageDeclaration;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.body.Parameter;
import com.github.javaparser.ast.body.VariableDeclarator;
import com.github.javaparser.ast.expr.FieldAccessExpr;
import com.github.javaparser.ast.expr.MethodCallExpr;
import com.github.javaparser.ast.expr.NameExpr;
import com.github.javaparser.ast.expr.ObjectCreationExpr;


import java.io.*;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * author: GLH
 * date:   2021-04-03
 * 该类的目的是提取每个源代码文件中的类名、方法名和变量名，并将其输出到json文件中
 */
public class SourceCodeInfoExtractor {

    public void extractMainInfo(String source, String target) {
        Scanner sc = new Scanner(System.in);
        try {
            // 读入整个文件，后续用来找注释
            ArrayList<String> contents = new ArrayList<>();
            BufferedReader reader = new BufferedReader(new FileReader(source));
            String line;
            while ((line = reader.readLine()) != null) {
                contents.add(line.trim());
            }

            // 先进行解析
            CompilationUnit cu = StaticJavaParser.parse(new FileInputStream(source));

            // 收集数据
            List<String> classORInterfaceNames = new ArrayList<>();
            cu.findAll(ClassOrInterfaceDeclaration.class).forEach(e -> classORInterfaceNames.add(e.getNameAsString()));

            List<String> declareMethodNames    = new ArrayList<>();
            cu.findAll(MethodDeclaration.class).forEach(e -> declareMethodNames.add(e.getNameAsString()));

            List<String> callMethodNames       = new ArrayList<>();
            cu.findAll(MethodCallExpr.class).forEach(e -> callMethodNames.add(e.getNameAsString()));

            List<String> constructorNames      = new ArrayList<>();
            cu.findAll(ObjectCreationExpr.class).forEach(e -> constructorNames.add(e.getTypeAsString()));

            List<String> declareVariableNames  = new ArrayList<>();
            cu.findAll(VariableDeclarator.class).forEach(e -> declareVariableNames.add(e.getNameAsString()));

            List<String> useVariableNames      = new ArrayList<>();
            cu.findAll(NameExpr.class).forEach(e -> useVariableNames.add(e.getNameAsString()));

            List<String> useFieldNames         = new ArrayList<>();
            cu.findAll(FieldAccessExpr.class).forEach(e -> useFieldNames.add(e.getNameAsString()));

            List<String> params                = new ArrayList<>();
            cu.findAll(Parameter.class).forEach(e -> params.add(e.getNameAsString()));

            List<String> packageNames          = new ArrayList<>();
            cu.findAll(PackageDeclaration.class).forEach(e -> packageNames.add(e.getNameAsString()));

            List<String> importFiles           = new ArrayList<>();
            cu.findAll(ImportDeclaration.class).forEach(e -> importFiles.add(e.getNameAsString()));

            List<String> extendORImplementFiles= new ArrayList<>();
            cu.findAll(ClassOrInterfaceDeclaration.class).forEach(t -> {
                t.getExtendedTypes().forEach(e -> extendORImplementFiles.add(e.toString()));
                t.getImplementedTypes().forEach(e -> extendORImplementFiles.add(e.toString()));
            });

            // 聚合变量和方法
            List<String> variables = new ArrayList<>();
            List<String> methods = new ArrayList<>();

            variables.addAll(declareVariableNames);
            variables.addAll(useVariableNames);
            variables.addAll(useFieldNames);
            variables.addAll(params);

            methods.addAll(declareMethodNames);
            methods.addAll(callMethodNames);
            methods.addAll(constructorNames);

            Map<String, Map<String, String>> methodBody = new HashMap<>();
            // 找到每个单独的方法，并找到其对应的注释
            cu.findAll(MethodDeclaration.class).forEach(md -> {
                Map<String, String> methodDetail = new HashMap<>();

                String methodName = md.getDeclarationAsString();
                methodDetail.put("methodName", methodName);

                if (md.getBody().isPresent()) {
                    methodDetail.put("methodBody", md.getBody().get().toString().replaceAll("\\/\\*[\\w\\W]*?\\*\\/|\\/\\/.*",""));
                } else {
                    methodDetail.put("methodBody", "");
                }


                // 记录方法所在的行
                int start = md.getBegin().get().line, end = md.getEnd().get().line;

                // 先收集与方法有关的行
                StringBuilder sb = new StringBuilder();
                // 向前寻找方法前的注释
                int i = Math.max(start - 2,0);
                for (; i >= 0; i--) {
                    if (contents.get(i).startsWith("*") || contents.get(i).startsWith("/*") || contents.get(i).startsWith("//")) {
                        continue;
                    } else {
                        i++;
                        break;
                    }
                }

                // 方法中寻找
                for (; i < md.getEnd().get().line; i++) {
                    sb.append(contents.get(i).trim()).append('\n');
                }

                // 正则匹配出所有注释
                StringBuilder comments = new StringBuilder();
                String regex = "\\/\\*[\\w\\W]*?\\*\\/|\\/\\/.*";
                Pattern p =  Pattern.compile(regex);
                Matcher m = p.matcher(sb.toString());
                while (m.find()) {
                    comments.append(sb.substring(m.start(), m.end())).append("\n");
                }
                methodDetail.put("comments", comments.toString());
                methodBody.put(methodName, methodDetail);
//                System.out.println(comments.toString());
//                System.out.println("****************************************************");
            });

            Map<String, Object> data = new HashMap<>();
            data.put("ClassORInterfaceName", classORInterfaceNames);
            data.put("methods", methods);
            data.put("variables", variables);
            data.put("package", packageNames);
            data.put("import", importFiles);
            data.put("extendORImplementFiles", extendORImplementFiles);
            data.put("methodsBody", methodBody);
            JSONObject json = new JSONObject(data);
            String pretty = JSON.toJSONString(json, SerializerFeature.PrettyFormat, SerializerFeature.WriteMapNullValue,
                    SerializerFeature.WriteDateUseDateFormat);
            PrintStream ps = new PrintStream(new FileOutputStream(target));
            ps.println(pretty);
        } catch (Exception e) {
            System.out.println(source);
            e.printStackTrace();
        }
    }

    public static void main(String[] args) {
        SourceCodePreprocessor scp = new SourceCodePreprocessor();
        scp.generateJSON("data/swt/src/accessibility/Accessible.java", "test.json");
    }
}
