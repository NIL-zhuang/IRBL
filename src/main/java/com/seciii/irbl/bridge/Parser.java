package com.seciii.irbl.bridge;

import java.util.Scanner;
import java.util.regex.Pattern;
import java.util.NoSuchElementException;

public class Parser {

    /**
     * Java读取命令行部分的运行状态 变为false则终止
     */
    private static boolean state;

    /**
     * 用于监听用户在console输入的指令
     */
    public static void terminal() {
        state = true;
        System.out.println("Starting....................................................................\n");
        System.out.println("        **************    ***********         *************           ******\n"
                + "           *********     ****      ****      *****       ***         ******\n"
                + "            ******      ****        ****    *****        ****       ******\n"
                + "           ******      ****         ***    *****       *****       ******\n"
                + "          ******      ***************     *****************       ******\n"
                + "         ******      **********          *****         *****     ******\n"
                + "        ******      ******  ****        *****          ******   ******\n"
                + "     *********     ******    *****     *****          *****    *******************\n"
                + "  **************  ******      ******  ******************      *********************\n");
        System.out.println("Loading complete! Welcome to IRBL --");
        System.out.println("                         --@Power by khyyyds group from NJU Software Institute\n\n");
        while (state) {
            resolutionCommand(readCommand());
        }
    }

    /**
     * 用于读取用户输入的指令
     *
     * @return String
     */
    private static String readCommand() {
        System.out.print("IRBL >");
        try {
            Scanner sc = new Scanner(System.in);
            sc.useDelimiter("\n");
            return sc.nextLine();
        } catch (NoSuchElementException e) {
            return null;
        }
    }

    /**
     * 用于解析用户输入的指令
     *
     * @param command
     */
    public static void resolutionCommand(String command) {
        if (command == null) {
            state = false;
            return;
        }

        String[] inputs = command.split(" ");

        if (inputs.length > 2) {
            System.out.println("Error: Can't resolve your parameter ");
        }

        switch (inputs[0]) {
            case "prep":
            case "preprocess":
            case "p":
            case "/p":
                if (inputs.length > 1) {
                    System.out.println("Error: Can't resolve your parameter ");
                } else {
                    preprocess();
                }

                break;

            case "dw":
            case "/d":
            case "defineWeight":
            case "define weight":
                if (inputs.length > 1) {
                    System.out.println("Error: Can't resolve your parameter ");
                } else {
                    defineWeight();
                }

                break;

            case "cs":
            case "/c":
            case "calculateSimilarity":
                if (inputs.length > 1) {
                    System.out.println("Error: Can't resolve your parameter ");
                } else {
                    calculateSimilarity();
                }

                break;

            case "pr":
            case "/pr":
            case "printResult":
                if (inputs.length == 2 && Pattern.compile("^[-\\+]?[\\d]*$").matcher(inputs[1]).matches()) {
                    printResult(Integer.parseInt(inputs[1]));
                } else if (inputs.length == 1) {
                    printResult(5);
                } else {
                    System.out.println("Error: The parameter <num> is a number. Please input required parameter. ");
                }

                break;
            case "/a":
            case "all":
            case "doall":
                if (inputs.length == 2 && Pattern.compile("^[\\d]*$").matcher(inputs[1]).matches()) {
                    doAll(Integer.parseInt(inputs[1]));
                } else if (inputs.length == 1) {
                    doAll(5);
                } else {
                    System.out.println("Error: The parameter <num> is a number. Please input required parameter. ");
                }

                break;

            case "exit":
            case "EXIT":
            case "Exit":
            case "q":
            case "Q":
            case "quit":
                if (inputs.length > 1) {
                    System.out.println("Error: Can't resolve your parameter ");
                } else {
                    exit();
                }
                break;

            case "\\h":
            case "/h":
            case "h":
            case "help":
                if (inputs.length > 1) {
                    System.out.println("Error: Can't resolve your parameter ");
                } else {
                    printCommand();
                }
                break;

            case "\n":
            case "\t":
            case "":
            case " ":
                break;

            default:
                error(command);
                break;
        }
    }

    private static void preprocess() {
        String[] args = new String[0];
        PythonCaller pythonCaller1 = new PythonCaller("bug_preprocess.py", args);
        pythonCaller1.exec();
        PythonCaller pythonCaller2 = new PythonCaller("code_preprocess.py", args);
        pythonCaller2.exec();
        System.out.println("Response : Preprocessor Success!");
    }

    private static void defineWeight() {
        System.out.println(
                "     *********************      **********************                 ****************      *************            **********************\n"
                        + "    *********************      **********************                   **************      ****************         **********************\n"
                        + "          ******              ******                                       ******          *****        ******      ******\n"
                        + "         ******              *********************    **************      ******          *****          ******    *********************\n"
                        + "        ******              ********************     **************      ******          *****          ******    ********************\n"
                        + "       ******              ******                                       ******          *****         ******     ******  \n"
                        + "      ******              ******                                       ******          *****       *******      ******\n"
                        + "     ******              ******                                   *************       *****     ******         ******\n"
                        + "    ******              ******                                  ****************     *************            ******\n");
        String[] args = new String[0];
        PythonCaller pythonCaller1 = new PythonCaller("weight_definer.py", args);
        pythonCaller1.exec();
        PythonCaller pythonCaller2 = new PythonCaller("bug2vec.py", args);
        pythonCaller2.exec();
        System.out.println("Response : Define Weight Success!");
    }

    private static void calculateSimilarity() {
        String[] args = new String[0];
        PythonCaller pythonCaller = new PythonCaller("simi_calculator.py", args);
        pythonCaller.exec();
        System.out.println("Response : Calculate Similarity Success!");
    }

    private static void printResult(int num) {
        String[] args = new String[]{String.valueOf(num)};
        PythonCaller pythonCaller = new PythonCaller("result_printer.py", args);
        pythonCaller.exec();
        System.out.println("Response : Print Result Success!");
    }

    private static void doAll(int num) {
        System.out.println("..............................................................................");
        preprocess();
        defineWeight();
        calculateSimilarity();
        printResult(num);
        System.out.println("Finished : All of the modules have finished!\n");
    }

    private static void exit() {
        System.out.println("Bye!");
        state = false;
    }

    private static void printCommand() {
        System.out.println("/a  <num>     推荐的默认命令选项，将data文件夹中的项目文件进行完整流程的处理，并输出结果");
        System.out.println("/p            对项目文件进行预处理");
        System.out.println("/d            进行权重计算，需要先经过预处理");
        System.out.println("/c            计算相似度，需要先经过预处理");
        System.out.println("/pr <num>     打印结果");
        System.out.println("\n有关工具的详细信息，可以通过参考文档进行进一步了解        @by  khyyyds\n");
    }

    private static void error(String command) {
        System.out.println("Error : Your command \"" + command + "\" is unrecognizable, please check your input.");
        System.out.println("     -- You can input </h> or <help> to know how to use me --\n");
    }

}
