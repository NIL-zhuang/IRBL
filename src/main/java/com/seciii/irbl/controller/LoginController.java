package com.seciii.irbl.controller;

import com.seciii.irbl.po.User;
import com.seciii.irbl.vo.ResponseVO;
import com.seciii.irbl.vo.UserForm;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/user")
public class LoginController {

    @PostMapping("/login")
    public ResponseVO login(@RequestBody UserForm userForm) {
        System.out.println(userForm.getUserName() + " " + userForm.getPassword());
        User user = new User();
        return ResponseVO.buildSuccess();
    }
}
