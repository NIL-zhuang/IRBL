package com.seciii.irbl;

import com.seciii.irbl.bridge.Parser;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

import java.io.IOException;

@SpringBootApplication
public class IrblApplication {

    public static void main(String[] args) {
        // 暂时不需要启动SpringBoot框架/h
        SpringApplication.run(IrblApplication.class, args);

//        Parser.terminal();
    }

}
