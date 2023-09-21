package com.chatbot.medison.controller;

import com.chatbot.medison.dao.SupplementDAO;
import com.chatbot.medison.dto.Supplement;
import lombok.extern.log4j.Log4j2;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

import java.util.List;

@Controller
@RequestMapping("/")
@Log4j2
public class ChatController {

    @Autowired
    SupplementDAO supplementDAO;

    //홈화면
    @GetMapping("home")
    private String aa() {

        return "home";
    }

    //메인화면
    @GetMapping("main")
    private String bb(Model model) {
        List<Supplement> list = supplementDAO.doSelect();
        System.out.println(list);
        model.addAttribute("list", list);
        return "main";
    }

    @GetMapping("detail")
    private String cc(Model model) {

        return "detail";
    }
}
