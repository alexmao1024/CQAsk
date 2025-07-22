"use client"


import { Alert, Layout, Select, Space, theme } from 'antd'
import Search from 'antd/es/input/Search'
import { useState } from 'react'
import { getCadDownload as downloadCadFile, getCadShapes as getCadObject } from './api/cad'
import CadViewer from './components/cad-viewer'
import ConversationHistory from './components/conversation-history'
import WelcomeScreen from './components/welcome-screen'
const { Content, } = Layout



export default function Home() {
  const {
    token: { colorBgContainer },
  } = theme.useToken()

  const [cadShapes, setCadShapes] = useState([])
  const [isError, setIsError] = useState(false)
  const [errorMessage, setErrorMessage] = useState("")
  const [cadID, setCadID] = useState<string>()
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  // const [UUID, setUUID] = useState<string>()

  const onSearch = async (value: string) => {
    if (!value.trim()) return
    
    try {
      setIsLoading(true)
      setIsError(false)
      setErrorMessage("")
      
      const cadObject = await getCadObject(value, conversationId)
      
      // 更新状态
      setCadShapes(cadObject.shapes)
      setCadID(cadObject.id)
      setConversationId(cadObject.conversation_id)
      
    } catch (error) {
      console.error("Error:", error)
      setIsError(true)
      setErrorMessage(error instanceof Error ? error.message : "Unknown error occurred")
    } finally {
      setIsLoading(false)
    }
  }

  const onNewConversation = () => {
    setConversationId(null)
    setCadShapes([])
    setCadID(undefined)
    setIsError(false)
    setErrorMessage("")
  }

  const onSelectHistoryResult = (result: any) => {
    if (result.error) {
      setIsError(true)
      setErrorMessage(result.error)
      return
    }
    
    // 设置历史结果到当前显示
    setCadShapes(result.shapes)
    setCadID(result.id)
    setConversationId(result.conversation_id)
    setIsError(false)
    setErrorMessage("")
  }

  const onExampleClick = (example: string) => {
    // 点击示例时自动触发搜索
    onSearch(example)
  }

  const onDownload = async (file_type: string) => {
    console.log(cadID, file_type)
    if (cadID && (file_type === "stl" || file_type === "step")) {
      await downloadCadFile(cadID, file_type as "stl" | "step")
    }
  }

  return (
    <Layout style={{ height: "100vh" }}>
      <div style={{ display: 'flex', height: '100%' }}>
        {/* 左侧历史对话栏 */}
        <div style={{ display: 'flex' }}>
          <ConversationHistory 
            onSelectResult={onSelectHistoryResult}
            currentConversationId={conversationId || undefined}
          />
        </div>

        {/* 右侧主要内容区 */}
        <Layout style={{ flex: 1, minWidth: 0 }}>
          <Space wrap style={{ padding: '10px' }}>
            <Select
              placeholder='Download'
              value={undefined}
              style={{ width: 120 }}
              onChange={onDownload}
              disabled={!cadID}
              options={[
                { value: 'py', label: 'Cadquery PY' },
                { value: 'step', label: 'STEP' },
                { value: 'stl', label: 'STL' },
                { value: 'amf', label: 'AMF' },
                { value: '3mf', label: '3MF' },
                { value: 'vrml', label: 'VRML' },
              ]}
            />
            
            <button 
              onClick={onNewConversation}
              style={{
                padding: '6px 15px',
                background: '#1890ff',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer'
              }}
            >
              新对话
            </button>
            
            {conversationId && (
              <span style={{ color: '#666', fontSize: '12px' }}>
                对话ID: {conversationId.slice(0, 8)}...
              </span>
            )}
          </Space>

          <Layout style={{ padding: '0 24px 24px' }}>
            <Content
              style={{
                margin: 0,
                minHeight: 280,
              }}
            >
              {cadShapes && Array.isArray(cadShapes) && cadShapes.length > 0 ? (
                <CadViewer cadShapes={cadShapes} />
              ) : (
                <WelcomeScreen onExampleClick={onExampleClick} />
              )}
            </Content>

            {
              isError ? (
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Alert
                    message="Error Generating"
                    description={errorMessage || "Please try again. To debug check logs and 'generated' directory for latest file"}
                    type="error"
                  />
                </Space>
              ) : null
            }

            <Search 
              placeholder={conversationId ? "继续对话..." : "输入CAD设计需求..."} 
              size="large" 
              onSearch={onSearch}
              loading={isLoading}
            />
          </Layout>
        </Layout>
      </div>
    </Layout>
  )
}

function Project() {
  throw new Error('Function not implemented.')
}


