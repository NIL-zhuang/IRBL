package com.seciii.irbl.bridge;


import com.seciii.irbl.PathGenerator;

import java.io.*;


public class PythonCaller {
    private String pyPath = ""; //.py文件路径
    private final String[] args; // 传给python程序的参数
    private final Runtime runtime;

    private void read(InputStream is, PrintStream ps) {
        try {
            BufferedReader reader = new BufferedReader(new InputStreamReader(is));
            String line;
            while ((line = reader.readLine()) != null) {
                ps.println(line);
            }
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            try {
                is.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    public PythonCaller(String file, String[] args) {
        String base = PathGenerator.generatePath(new String[]{"src", "main", "python", "irbl"});
        pyPath = base + file;
        this.args = args;
        runtime = Runtime.getRuntime();
    }

    public void exec() {
        System.out.println(System.getenv());
        StringBuilder codeBuilder = new StringBuilder("python ");
        codeBuilder.append(pyPath).append(' ');
        if (args != null)
            for (String arg : args) {
                codeBuilder.append(arg);
            }
        try {
            String code = codeBuilder.toString();
            System.out.println("Exec: " + code);
            Process process = runtime.exec(code);


            //获取进程的标准输入流
            final InputStream is1 = process.getInputStream();
            //获取进城的错误流
            final InputStream is2 = process.getErrorStream();
            //启动两个线程，一个线程负责读标准输出流，另一个负责读标准错误流
            new Thread(() -> {
                BufferedReader br1 = new BufferedReader(new InputStreamReader(is1));
                try {
                    String line1 = null;
                    while ((line1 = br1.readLine()) != null) {
                        if (line1 != null){
                            System.out.println(line1);
                        }
                    }
                } catch (IOException e) {
                    e.printStackTrace();
                }
                finally{
                    try {
                        is1.close();
                    } catch (IOException e) {
                        e.printStackTrace();
                    }
                }
            }).start();

            new Thread(() -> {
                BufferedReader br2 = new  BufferedReader(new  InputStreamReader(is2));
                try {
                    String line2 = null ;
                    while ((line2 = br2.readLine()) !=  null ) {
                        if (line2 != null){
                            System.out.println(line2);
                        }
                    }
                } catch (IOException e) {
                    e.printStackTrace();
                }
                finally{
                    try {
                        is2.close();
                    } catch (IOException e) {
                        e.printStackTrace();
                    }
                }
            }).start();

            process.waitFor();
//            read(process.getInputStream(), System.out);
//            read(process.getErrorStream(), System.err);
            process.destroy();
        } catch (IOException | InterruptedException ioe) {
            ioe.printStackTrace();
        }
    }
}
