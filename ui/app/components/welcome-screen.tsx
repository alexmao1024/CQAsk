"use client"

import { Card, Typography, Row, Col, Space } from 'antd'
import { 
  RocketOutlined, 
  BulbOutlined, 
  ToolOutlined, 
  HistoryOutlined,
  MessageOutlined,
  DownloadOutlined 
} from '@ant-design/icons'

const { Title, Paragraph, Text } = Typography

interface WelcomeScreenProps {
  onExampleClick?: (example: string) => void
}

export default function WelcomeScreen({ onExampleClick }: WelcomeScreenProps) {
  const features = [
    {
      icon: <MessageOutlined style={{ fontSize: '32px', color: '#1890ff' }} />,
      title: '智能对话',
      description: '使用自然语言描述你的设计需求，AI助手会生成相应的CAD代码'
    },
    {
      icon: <ToolOutlined style={{ fontSize: '32px', color: '#52c41a' }} />,
      title: '实时预览',
      description: '生成的3D模型会立即在右侧渲染，支持旋转、缩放等交互操作'
    },
    {
      icon: <HistoryOutlined style={{ fontSize: '32px', color: '#faad14' }} />,
      title: '历史管理',
      description: '左侧历史栏记录所有对话，可随时查看和恢复之前的设计版本'
    },
    {
      icon: <BulbOutlined style={{ fontSize: '32px', color: '#eb2f96' }} />,
      title: '迭代优化',
      description: '可以持续改进设计，AI会根据你的反馈调整模型参数'
    },
    {
      icon: <DownloadOutlined style={{ fontSize: '32px', color: '#722ed1' }} />,
      title: '多格式导出',
      description: '支持导出STL、STEP等多种CAD格式，便于后续加工制造'
    },
    {
      icon: <RocketOutlined style={{ fontSize: '32px', color: '#f5222d' }} />,
      title: '快速上手',
      description: '无需学习复杂的CAD软件，用聊天的方式就能完成3D设计'
    }
  ]

  const examples = [
    "创建一个直径50mm、高度30mm的圆柱体",
    "设计一个100x50x20mm的矩形盒子，顶面开一个直径10mm的孔",
    "制作一个模数为2、齿数为30的直齿轮",
    "设计一个简单的手机支架",
    "创建一个螺旋弹簧，螺距为5mm",
    "制作一个六角螺母，对边距离20mm"
  ]

  return (
    <div style={{ 
      height: '100%', 
      background: '#f8f9fa',
      padding: '20px 20px 40px 20px',
      overflow: 'auto'
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto', width: '100%' }}>
        {/* 标题区域 */}
        <div style={{ textAlign: 'center', marginBottom: '40px', paddingTop: '20px' }}>
          <Title 
            level={1} 
            style={{ 
              color: '#1890ff', 
              fontSize: 'clamp(32px, 8vw, 48px)', 
              marginBottom: '16px',
              fontWeight: 'bold'
            }}
          >
            🚀 CQAsk
          </Title>
          <Title 
            level={2} 
            style={{ 
              color: '#595959', 
              fontWeight: 'normal', 
              marginBottom: '16px',
              fontSize: 'clamp(18px, 4vw, 24px)'
            }}
          >
            AI驱动的CAD设计助手
          </Title>
          <Paragraph style={{ 
            color: '#8c8c8c', 
            fontSize: 'clamp(14px, 3vw, 18px)',
            maxWidth: '600px',
            margin: '0 auto'
          }}>
            用自然语言描述你的想法，让AI帮你创建3D模型
          </Paragraph>
        </div>

        {/* 功能特性 */}
        <Row gutter={[24, 24]} style={{ marginBottom: '40px' }}>
          {features.map((feature, index) => (
            <Col xs={24} sm={12} lg={8} key={index}>
              <Card 
                hoverable
                style={{ 
                  height: '100%',
                  borderRadius: '12px',
                  border: '1px solid #f0f0f0',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
                  transition: 'all 0.3s'
                }}
                bodyStyle={{ padding: '24px' }}
              >
                <Space direction="vertical" style={{ width: '100%' }} align="center">
                  <div style={{ 
                    padding: '12px',
                    borderRadius: '50%',
                    background: '#f8f9fa',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}>
                    {feature.icon}
                  </div>
                  <Title level={4} style={{ 
                    color: '#262626', 
                    textAlign: 'center', 
                    margin: '12px 0 8px 0',
                    fontSize: 'clamp(16px, 3vw, 18px)'
                  }}>
                    {feature.title}
                  </Title>
                  <Text style={{ 
                    color: '#8c8c8c', 
                    textAlign: 'center', 
                    display: 'block',
                    lineHeight: '1.6',
                    fontSize: 'clamp(12px, 2.5vw, 14px)'
                  }}>
                    {feature.description}
                  </Text>
                </Space>
              </Card>
            </Col>
          ))}
        </Row>

        {/* 示例命令 */}
        <Card 
          style={{ 
            borderRadius: '12px',
            border: '1px solid #f0f0f0',
            boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
            marginBottom: '32px'
          }}
          bodyStyle={{ padding: '32px' }}
        >
          <Title level={3} style={{ 
            color: '#262626', 
            textAlign: 'center', 
            marginBottom: '24px',
            fontSize: 'clamp(18px, 4vw, 22px)'
          }}>
            💡 试试这些示例
          </Title>
          <Row gutter={[16, 16]}>
            {examples.map((example, index) => (
              <Col xs={24} sm={12} lg={12} key={index}>
                <div 
                  style={{
                    padding: '16px 20px',
                    background: '#fafafa',
                    borderRadius: '8px',
                    border: '1px solid #e8e8e8',
                    cursor: 'pointer',
                    transition: 'all 0.3s',
                    color: '#595959',
                    fontSize: 'clamp(12px, 2.5vw, 14px)',
                    lineHeight: '1.5'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = '#e6f7ff'
                    e.currentTarget.style.borderColor = '#1890ff'
                    e.currentTarget.style.color = '#1890ff'
                    e.currentTarget.style.transform = 'translateY(-2px)'
                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(24,144,255,0.15)'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = '#fafafa'
                    e.currentTarget.style.borderColor = '#e8e8e8'
                    e.currentTarget.style.color = '#595959'
                    e.currentTarget.style.transform = 'translateY(0)'
                    e.currentTarget.style.boxShadow = 'none'
                  }}
                  onClick={() => onExampleClick && onExampleClick(example)}
                >
                  "{example}"
                </div>
              </Col>
            ))}
          </Row>
        </Card>

        {/* 开始提示 */}
        <div style={{ textAlign: 'center' }}>
          <Title level={4} style={{ 
            color: '#262626', 
            marginBottom: '12px',
            fontSize: 'clamp(16px, 3.5vw, 20px)'
          }}>
            🎯 开始你的第一个设计
          </Title>
          <Paragraph style={{ 
            color: '#8c8c8c', 
            fontSize: 'clamp(12px, 2.5vw, 16px)',
            maxWidth: '500px',
            margin: '0 auto'
          }}>
            在下方的搜索框中输入你的设计需求，或点击上方示例快速开始
          </Paragraph>
        </div>
      </div>
    </div>
  )
} 