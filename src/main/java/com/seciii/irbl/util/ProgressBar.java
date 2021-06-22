package com.seciii.irbl.util;

public class ProgressBar {
    private final int PROGRESS_SIZE;
    private final int SIZE = 50;

    public ProgressBar(int PROGRESS_SIZE) {
        this.PROGRESS_SIZE = PROGRESS_SIZE;
    }

    public void init(String prompt) {
        System.out.printf("%-10s", prompt);
        String unFinish = getNChar(SIZE, '-');
        String target = String.format("%3d%%[%s]", 0, unFinish);
        System.out.print(target);
    }

    public void printProgress(int index) {
        String finish = getNChar(index * SIZE / PROGRESS_SIZE, '█');
        String unFinish = getNChar(SIZE - index * SIZE / PROGRESS_SIZE, '─');

        String target = String.format("%3d%%├%s%s┤", index * 100 / PROGRESS_SIZE, finish, unFinish);
        System.out.print(getNChar(SIZE + 6, '\b'));
        System.out.print(target);
    }

    private String getNChar(int num, char ch) {
        StringBuilder builder = new StringBuilder();
        for (int i = 0; i <num; i++) {
            builder.append(ch);
        }
        return builder.toString();
    }

    public static void main(String[] args) throws InterruptedException {
        ProgressBar progressBar = new ProgressBar(50);
        progressBar.init("预处理:");
        for (int i = 0; i <= 100; i++) {
            progressBar.printProgress(i);
            Thread.sleep(50);
        }
    }
}
