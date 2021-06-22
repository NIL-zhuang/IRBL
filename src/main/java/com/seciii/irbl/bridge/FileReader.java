package com.seciii.irbl.bridge;

import java.io.File;
import java.util.ArrayList;

@Deprecated
/**
 * @Author HX
 * @Date 2021/3/13
 * 用于读取文件路径下所有文件名，只返回其中的路径名
 */
public class FileReader {

    /**
     * 路径名存放数组
     */
    ArrayList<String> dirAllStrArr = new ArrayList<String>();

    /**
     * 单独存放xml文件路径名
     */
    ArrayList<String> dirAllXml = new ArrayList<String>();

    /**
     * 递归深度
     */
    int depth = 0;

    /**
     * 查询当前路径下的文件夹
     * @param dirFile
     * @return ArrayList
     * @throws Exception
     */
    public ArrayList<String> Dir(File dirFile) throws Exception {
        ArrayList<String> dirStrArr = new ArrayList<String>();

        if (dirFile.exists()) {
            // 直接取出利用listFiles()把当前路径下的所有文件夹、文件存放到一个文件数组
            File[] files = dirFile.listFiles();
            assert files != null;
            for (File file : files) {
                // 如果传递过来的参数dirFile是以文件分隔符，也就是/或者\结尾，则如此构造
                if(file.isDirectory())
                    continue;
                if (dirFile.getPath().endsWith(File.separator)) {
                    dirStrArr.add("\""+dirFile.getPath() + file.getName()+"\"");
                } else {
                    // 否则，如果没有文件分隔符，则补上一个文件分隔符，再加上文件名，才是路径
                    dirStrArr.add("\""+dirFile.getPath() + File.separator
                            + file.getName()+"\"");
                }
            }
        }
        return dirStrArr;
    }

    /**
     * 递归获取文件夹中的项目
     * @param dirFile
     * @throws Exception
     */
    public String DirAll(File dirFile) throws Exception {

        depth++;

        if (dirFile.exists()) {
            File files[] = dirFile.listFiles();
            for (File file : files) {

                if (file.isDirectory()) {
                    DirAll(file);
                } else {
                    if(file.getName().substring(file.getName().lastIndexOf(".") + 1).equals("xml")){
                        if (dirFile.getPath().endsWith(File.separator)) {
                            dirAllXml.add("\""+dirFile.getPath() + file.getName()+"\"");
                        } else {
                            dirAllXml.add("\""+dirFile.getPath() + File.separator
                                    + file.getName()+"\"");
                        }
                    }
                    else{
                        if (dirFile.getPath().endsWith(File.separator)) {
                            dirAllStrArr.add("\""+dirFile.getPath() + file.getName()+"\"");
                        } else {
                            dirAllStrArr.add("\""+dirFile.getPath() + File.separator
                                    + file.getName()+"\"");
                        }
                    }
                }
            }
        }
        depth--;

        if(depth==0){
            return String.join(",",dirAllXml) + " " + String.join(",",dirAllStrArr);
        }else
            return null;
    }

}
