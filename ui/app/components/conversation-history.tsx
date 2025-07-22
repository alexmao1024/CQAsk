"use client"

import { useState, useEffect } from 'react'
import { Menu, Dropdown, Space, Button, Spin } from 'antd'
import type { MenuProps } from 'antd'
import { DownOutlined, MessageOutlined, HistoryOutlined } from '@ant-design/icons'
import { getConversations, getConversationDetail, getMessageResult } from '../api/cad'

interface ConversationSummary {
  id: string
  created_at: string
  title: string
  message_count: number
  assistant_responses: number
  current_object_id?: string
}

interface ConversationMessage {
  index: number
  role: string
  content: string
  timestamp: string
  object_id?: string
  error?: string
  has_result?: boolean
}

interface ConversationDetail {
  id: string
  created_at: string
  messages: ConversationMessage[]
  current_object_id?: string
}

interface ConversationHistoryProps {
  onSelectResult: (result: any) => void
  currentConversationId?: string
}

export default function ConversationHistory({ onSelectResult, currentConversationId }: ConversationHistoryProps) {
  const [conversations, setConversations] = useState<ConversationSummary[]>([])
  const [loading, setLoading] = useState(false)
  const [selectedConversation, setSelectedConversation] = useState<string | null>(null)
  const [conversationDetails, setConversationDetails] = useState<{ [key: string]: ConversationDetail }>({})

  // 加载对话列表
  useEffect(() => {
    loadConversations()
  }, [])

  const loadConversations = async () => {
    try {
      setLoading(true)
      const response = await getConversations()
      setConversations(response.conversations || [])
    } catch (error) {
      console.error('Failed to load conversations:', error)
    } finally {
      setLoading(false)
    }
  }

  // 加载特定对话的详细信息
  const loadConversationDetail = async (conversationId: string) => {
    if (conversationDetails[conversationId]) return // 已经加载过

    try {
      const detail = await getConversationDetail(conversationId)
      setConversationDetails(prev => ({
        ...prev,
        [conversationId]: detail
      }))
    } catch (error) {
      console.error('Failed to load conversation detail:', error)
    }
  }

  // 选择特定消息结果
  const selectMessageResult = async (conversationId: string, messageIndex: number) => {
    try {
      const result = await getMessageResult(conversationId, messageIndex)
      if (result.error) {
        console.error('Error getting message result:', result.error)
        return
      }
      onSelectResult(result)
    } catch (error) {
      console.error('Failed to get message result:', error)
    }
  }

  // 创建下拉菜单项
  const createDropdownMenu = (conversationId: string): MenuProps => {
    const detail = conversationDetails[conversationId]
    if (!detail) return { items: [] }

    const items = detail.messages
      .filter(msg => msg.role === 'assistant' && msg.has_result)
      .map(msg => ({
        key: `${conversationId}-${msg.index}`,
        label: (
          <div style={{ maxWidth: '300px' }}>
            <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>
              第 {Math.floor(msg.index / 2) + 1} 个回复
            </div>
            <div style={{ fontSize: '12px', color: '#666', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              {new Date(msg.timestamp).toLocaleString()}
            </div>
            {msg.error && (
              <div style={{ fontSize: '12px', color: '#f50', marginTop: '2px' }}>
                有错误
              </div>
            )}
          </div>
        ),
        onClick: () => selectMessageResult(conversationId, msg.index)
      }))

    return { items }
  }

  return (
    <div style={{ 
      width: '100%',
      maxWidth: '320px',
      minWidth: '280px',
      height: '100vh', 
      borderRight: '1px solid #f0f0f0', 
      backgroundColor: '#ffffff',
      display: 'flex',
      flexDirection: 'column'
    }}>
      {/* 标题栏 */}
      <div style={{ 
        padding: '16px', 
        borderBottom: '1px solid #f0f0f0',
        backgroundColor: '#fff'
      }}>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between' 
        }}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <HistoryOutlined style={{ marginRight: '8px', color: '#1890ff' }} />
            <span style={{ fontWeight: 'bold', fontSize: '16px' }}>历史对话</span>
          </div>
          <Button 
            size="small" 
            onClick={loadConversations}
            loading={loading}
          >
            刷新
          </Button>
        </div>
      </div>

      {/* 对话列表 */}
      <div style={{ flex: 1, overflow: 'auto', padding: '8px' }}>
        {loading && conversations.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '20px' }}>
            <Spin />
          </div>
        ) : conversations.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '20px', color: '#999' }}>
            暂无历史对话
          </div>
        ) : (
          conversations.map(conv => (
            <div 
              key={conv.id}
              style={{
                marginBottom: '8px',
                padding: '12px',
                backgroundColor: conv.id === currentConversationId ? '#e6f7ff' : '#fff',
                border: conv.id === currentConversationId ? '1px solid #1890ff' : '1px solid #f0f0f0',
                borderRadius: '6px',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                if (conv.id !== currentConversationId) {
                  e.currentTarget.style.backgroundColor = '#f5f5f5'
                }
              }}
              onMouseLeave={(e) => {
                if (conv.id !== currentConversationId) {
                  e.currentTarget.style.backgroundColor = '#fff'
                }
              }}
            >
              <div style={{ marginBottom: '8px' }}>
                <div style={{ 
                  fontWeight: 'bold', 
                  fontSize: '14px',
                  marginBottom: '4px',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap'
                }}>
                  {conv.title}
                </div>
                <div style={{ fontSize: '12px', color: '#999' }}>
                  {new Date(conv.created_at).toLocaleDateString()} • {conv.assistant_responses} 个回复
                </div>
              </div>

              {conv.assistant_responses > 0 && (
                <Dropdown
                  menu={createDropdownMenu(conv.id)}
                  onOpenChange={(open) => {
                    if (open) {
                      loadConversationDetail(conv.id)
                    }
                  }}
                  trigger={['click']}
                >
                  <Button 
                    size="small" 
                    style={{ width: '100%' }}
                    onClick={(e) => e.stopPropagation()}
                  >
                    <Space>
                      <MessageOutlined />
                      查看回复
                      <DownOutlined />
                    </Space>
                  </Button>
                </Dropdown>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
} 