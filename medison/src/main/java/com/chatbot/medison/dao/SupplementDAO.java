package com.chatbot.medison.dao;

import com.chatbot.medison.dto.Supplement;
import org.apache.ibatis.session.SqlSession;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public class SupplementDAO {

    @Autowired
    SqlSession sqlSession;

    public List<Supplement> doSelect(){
        return sqlSession.selectList("supplement.select");
    }
}
