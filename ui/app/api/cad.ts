import axios from "axios"
import { downloadAxiosResponse } from "../utils"

const BASE_URL = "http://127.0.0.1:5001"

export function getCadShapes(query: string, conversationId: string | null = null) {
  let config = {
    method: 'post',
    maxBodyLength: Infinity,
    url: `${BASE_URL}/cad`,
    headers: {
      'Content-Type': 'application/json',
    },
    data: {
      query,
      conversation_id: conversationId,
    },
  }

  return axios.request(config)
    .then(async (response) => {
      if (response.data.error) {
        throw new Error(response.data.error);
      }
      return response.data;
    })
    .catch((error) => {
      console.error("API Error:", error);
      throw error; // 将错误传递给调用者
    });
}


export function getCadDownload(id: string, file_type: "step" | "stl") {
  let config = {
    method: 'get' as const,
    maxBodyLength: Infinity,
    responseType: 'arraybuffer' as const,
    url: `${BASE_URL}/download`,
    headers: {
      "Content-Type": "application/json"
    },
    params: {
      id,
      file_type,
    },
  }

  return axios.request(config)
    .then(async (response) => {
      console.log(response)
      downloadAxiosResponse(`${id}.${file_type}`, response)
    })
    .catch((error) => {
      console.log(error)
    })
}

export function getConversations() {
  return axios.get(`${BASE_URL}/conversations`)
    .then(response => response.data)
    .catch(error => {
      console.error("Error getting conversations:", error)
      throw error
    })
}

export function getConversationDetail(conversationId: string) {
  return axios.get(`${BASE_URL}/conversation/${conversationId}`)
    .then(response => response.data)
    .catch(error => {
      console.error("Error getting conversation detail:", error)
      throw error
    })
}

export function getMessageResult(conversationId: string, messageIndex: number) {
  return axios.get(`${BASE_URL}/conversation/${conversationId}/message/${messageIndex}`)
    .then(response => response.data)
    .catch(error => {
      console.error("Error getting message result:", error)
      throw error
    })
}


