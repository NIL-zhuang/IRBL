package com.seciii.irbl.sourceCodePreprocess;

import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.NodeList;
import com.github.javaparser.metamodel.NodeMetaModel;
import com.github.javaparser.metamodel.PropertyMetaModel;

import java.util.List;

import static com.github.javaparser.utils.Utils.assertNotNull;
import static java.util.stream.Collectors.toList;

/**
 * author: Guo Lihua
 * date:   2021-03-31
 * 这个类是重写了原来javaparser中的XMLPrinter，将其进行了改写以能够生成正确格式的xml文档
 * 原来的版本没有解决单双引号不一致的问题
 */
public class MyXMLPrinter {
    private final boolean outputNodeType;

    public MyXMLPrinter(boolean outputNodeType) {
        this.outputNodeType = outputNodeType;
    }

    public String output(Node node) {
        StringBuilder output = new StringBuilder();
        output(node, "root", 0, output);
        return output.toString();
    }

    public void output(Node node, String name, int level, StringBuilder builder) {
        assertNotNull(node);
        NodeMetaModel metaModel = node.getMetaModel();
        List<PropertyMetaModel> allPropertyMetaModels = metaModel.getAllPropertyMetaModels();
        List<PropertyMetaModel> attributes = allPropertyMetaModels.stream().filter(PropertyMetaModel::isAttribute).filter(PropertyMetaModel::isSingular).collect(toList());
        List<PropertyMetaModel> subNodes = allPropertyMetaModels.stream().filter(PropertyMetaModel::isNode).filter(PropertyMetaModel::isSingular).collect(toList());
        List<PropertyMetaModel> subLists = allPropertyMetaModels.stream().filter(PropertyMetaModel::isNodeList).collect(toList());

        builder.append("<").append(name);
        if (outputNodeType) {
            builder.append(attribute("type", metaModel.getTypeName()));
        }

        for (PropertyMetaModel attributeMetaModel : attributes) {
            if (attributeMetaModel.getName().equals("type")) {
                builder.append(attribute("specificType", attributeMetaModel.getValue(node).toString()));
            } else {
                builder.append(attribute(attributeMetaModel.getName(), attributeMetaModel.getValue(node).toString()));
            }
        }
        builder.append(">");


        for (PropertyMetaModel subNodeMetaModel : subNodes) {
            Node value = (Node) subNodeMetaModel.getValue(node);
            if (value != null) {
                output(value, subNodeMetaModel.getName(), level + 1, builder);
            }
        }

        for (PropertyMetaModel subListMetaModel : subLists) {
            NodeList<? extends Node> subList = (NodeList<? extends Node>) subListMetaModel.getValue(node);
            if (subList != null && !subList.isEmpty()) {
                String listName = subListMetaModel.getName();
                builder.append("<").append(listName).append(">");
                String singular = listName.substring(0, listName.length() - 1);
                for (Node subListNode : subList) {
                    output(subListNode, singular, level + 1, builder);
                }
                builder.append(close(listName));
            }
        }
        builder.append(close(name));
    }

    private static String close(String name) {
        return "</" + name + ">";
    }

    private static String attribute(String name, String value) {
        return " " + name + "='" + change(value) + "'";
    }

    /**
     * 这个方法是新加的，需要对value中的引号做处理，这里直接删掉了
     * @param value 属性值
     * @return 去除掉单双引号的属性值
     */
    private static String change(String value) {
        return value.replaceAll("[^0-9a-zA-Z]J*"," ").replaceAll(" +"," ");
    }

    public static void print(Node node) {
        System.out.println(new MyXMLPrinter(true).output(node));
    }
}
