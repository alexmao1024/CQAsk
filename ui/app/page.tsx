"use client"


import { Alert, Layout, Select, Space, theme, Radio } from 'antd'
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
  const [cadData, setCadData] = useState<any>(null)

  // --- 状态重构 ---
  // activeMode: 当前UI和请求所使用的渲染模式。
  const [activeMode, setActiveMode] = useState<string>("3d");
  // isModeLocked: 模式是否被锁定，由会话是否存在决定。
  const [isModeLocked, setIsModeLocked] = useState<boolean>(false);
  // --- 状态重构结束 ---

  const onSearch = async (value: string) => {
    if (!value.trim()) return
    
    try {
      setIsLoading(true)
      setIsError(false)
      setErrorMessage("")
      
      // 请求总是使用 activeMode
      const cadObject = await getCadObject(value, conversationId, activeMode)
      
      // 请求成功后，更新所有状态
      setCadData(cadObject)
      setCadShapes(cadObject.shapes || [])
      setCadID(cadObject.id)
      setConversationId(cadObject.conversation_id)
      
      // 直接根据返回结果设置当前模式，并锁定
      setActiveMode(cadObject.render_mode);
      setIsModeLocked(true);
      
    } catch (error: any) {
      console.error("Error:", error)
      setIsError(true)
      const backendError = error.response?.data?.error || error.message;
      setErrorMessage(backendError || "发生了未知错误")
    } finally {
      setIsLoading(false)
    }
  }

  const onNewConversation = () => {
    // 重置所有会话状态
    setConversationId(null)
    setCadShapes([])
    setCadID(undefined)
    setCadData(null)
    setIsError(false)
    setErrorMessage("")
    
    // 解除模式锁定，允许用户再次选择
    setIsModeLocked(false);
  }

  const onSelectHistoryResult = (result: any) => {
    if (result.error) {
      setIsError(true)
      setErrorMessage(result.error)
      return
    }
    
    // 设置历史结果到当前显示
    setCadData(result)
    setCadShapes(result.shapes || [])
    setCadID(result.id)
    setConversationId(result.conversation_id)
    setIsError(false)
    setErrorMessage("")
    
    // 从历史记录恢复模式，并立即锁定
    if (result.render_mode) {
      setActiveMode(result.render_mode);
      setIsModeLocked(true);
    }
  }

  const onExampleClick = (example: string) => {
    onSearch(example)
  }

  const onDownload = async (file_type: string) => {
    console.log(cadID, file_type)
    if (cadID) {
      const validFormats = ["step", "stl", "obj", "3mf", "svg"]
      if (validFormats.includes(file_type)) {
        await downloadCadFile(cadID, file_type as "step" | "stl" | "obj" | "3mf" | "svg")
      }
    }
  }

  const getDownloadOptions = () => {
    const is2D = cadData && cadData.render_mode === "2d"
    
    if (is2D) {
      return [{ value: 'svg', label: 'SVG' }]
    } else {
      return [
        { value: 'step', label: 'STEP' },
        { value: 'stl', label: 'STL' },
        { value: 'obj', label: 'OBJ' },
        { value: '3mf', label: '3MF' },
      ]
    }
  }
  
  // 模式切换器仅在未锁定时调用
  const onRenderModeChange = (e: any) => {
    setActiveMode(e.target.value)
  }

  const renderContent = () => {
    if (!cadData) {
      return <WelcomeScreen onExampleClick={onExampleClick} />
    }

    if (cadData.render_mode === "2d") {
      return (
        <div style={{ 
          padding: '20px', 
          background: '#f5f5f5', 
          borderRadius: '8px',
          height: '70vh',
          overflow: 'auto',
          display: 'flex',
          flexDirection: 'column'
        }}>
          <h3>📐 2D CAD 图形</h3>
          
          {cadData.svg ? (
            <div style={{ 
              flex: 1,
              background: 'white', 
              padding: '15px', 
              borderRadius: '4px',
              border: '1px solid #d9d9d9',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              minHeight: '300px'
            }}>
              <div 
                dangerouslySetInnerHTML={{ __html: cadData.svg }}
                style={{ maxWidth: '100%', maxHeight: '100%' }}
              />
            </div>
          ) : (
            <div style={{ 
              flex: 1,
              background: 'white', 
              padding: '15px', 
              borderRadius: '4px',
              border: '1px solid #d9d9d9'
            }}>
              <div style={{ marginBottom: '10px', color: '#666', fontSize: '12px' }}>
                ⚠️ 图形渲染不可用，显示代码预览：
              </div>
              <pre style={{ 
                fontSize: '14px', 
                lineHeight: '1.5',
                margin: 0,
                whiteSpace: 'pre-wrap',
                wordWrap: 'break-word'
              }}>
                {cadData.code || '// 代码加载中...'}
              </pre>
            </div>
          )}
          
          <div style={{ marginTop: '15px', color: '#666', fontSize: '12px' }}>
            {/* eslint-disable-next-line react/no-unescaped-entities */}
            💡 提示：这是2D CAD图形渲染。如果您需要查看3D模型，请开始新对话并选择'3D渲染'模式。
            {cadData.note && (
              <div style={{ color: '#ff6b6b', marginTop: '5px' }}>
                注意：{cadData.note}
              </div>
            )}
            {cadData.generator && (
              <div style={{ color: '#52c41a', marginTop: '5px' }}>
                📊 生成器：{cadData.generator === 'schemdraw' ? 'SchemDraw (专业电路图)' : 
                         cadData.generator === 'cadquery' ? 'CadQuery (备选方案)' : 
                         '代码预览'}
              </div>
            )}
          </div>
        </div>
      )
    }

    if (cadShapes && Array.isArray(cadShapes) && cadShapes.length > 0) {
      return <CadViewer cadShapes={cadShapes} />
    }

    return <WelcomeScreen onExampleClick={onExampleClick} />
  }

  return (
    <Layout style={{ height: "100vh" }}>
      <div style={{ display: 'flex', height: '100%' }}>
        <ConversationHistory 
          onSelectResult={onSelectHistoryResult}
          currentConversationId={conversationId || undefined}
        />

        <Layout style={{ flex: 1, minWidth: 0 }}>
          <Space wrap style={{ padding: '10px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '14px', color: '#666' }}>渲染模式:</span>
              <Radio.Group 
                value={activeMode} 
                onChange={onRenderModeChange} 
                size="small"
                disabled={isModeLocked}
              >
                <Radio.Button value="3d">🎲 3D渲染</Radio.Button>
                <Radio.Button value="2d">📐 2D渲染</Radio.Button>
              </Radio.Group>
              {isModeLocked && (
                <span style={{ fontSize: '12px', color: '#ff9500' }}>
                  🔒 已锁定
                </span>
              )}
            </div>

            <Select
              placeholder='Download'
              value={undefined}
              style={{ width: 120 }}
              onChange={onDownload}
              disabled={!cadID}
              options={getDownloadOptions()}
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
              {renderContent()}
            </Content>

            {
              isError ? (
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Alert
                    message="生成过程中遇到问题"
                    description={
                      <div style={{ whiteSpace: 'pre-line' }}>
                        {errorMessage || "请重试。如需调试，请检查日志和'generated'目录中的最新文件"}
                      </div>
                    }
                    type="error"
                    style={{ marginBottom: '10px' }}
                  />
                </Space>
              ) : null
            }

            <Search 
              placeholder={conversationId ? "继续对话..." : `输入CAD设计需求... (当前: ${activeMode === '3d' ? '3D模型' : '2D图形'})`} 
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