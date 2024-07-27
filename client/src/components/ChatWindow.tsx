import React, { useState, useEffect, useCallback, useRef } from 'react';
import ChatMessage from './ChatMessage';
import { getSessionId, sendChatMessage, getChatStream, savePlan } from '@/lib/api';
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import {
  Menubar,
  MenubarContent,
  MenubarItem,
  MenubarMenu,
  MenubarSeparator,
  MenubarTrigger,
} from "@/components/ui/menubar";

interface Message {
  type: string;
  content: any;
  isBot: boolean;
}

interface ChatWindowProps {
  initialMessages: Message[];
  currentPlan: any;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ initialMessages, currentPlan }) => {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [appSessionId, setAppSessionId] = useState<string | null>(null);
  const [chatSessionId, setChatSessionId] = useState<string | null>(null);
  const messageBufferRef = useRef<Message | null>(null);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const eventSourceRef = useRef<EventSource | null>(null);
  const messageContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const fetchAppSessionId = async () => {
      const sessionId = await getSessionId();
      setAppSessionId(sessionId);
    };

    fetchAppSessionId();
  }, []);

  useEffect(() => {
    adjustTextareaHeight();
  }, [input]);

  const scrollToBottom = useCallback(() => {
    if (messageContainerRef.current) {
      messageContainerRef.current.scrollTop = messageContainerRef.current.scrollHeight;
    }
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const adjustTextareaHeight = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      const scrollHeight = textareaRef.current.scrollHeight;
      const lineHeight = parseInt(getComputedStyle(textareaRef.current).lineHeight);
      const maxHeight = lineHeight * 5; // 5 lines maximum
      const newHeight = Math.min(scrollHeight, maxHeight);
      textareaRef.current.style.height = `${newHeight}px`;
    }
  };

  const handleSendMessage = useCallback(async (message: string) => {
    if (!message.trim() || isLoading) return;

    setMessages(prevMessages => [...prevMessages, { type: 'text', content: message, isBot: false }]);
    setInput('');
    setIsLoading(true);

    if (message.trim().toLowerCase() === 'save_plan') {
      try {
        let plan_obj: object;
        if (typeof currentPlan === 'string') {
          plan_obj = JSON.parse(currentPlan);
        } else {
          plan_obj = currentPlan;
        }
        const response = await savePlan(plan_obj);
        setMessages(prevMessages => [...prevMessages, { type: 'text', content: response.message, isBot: true }]);
      } catch (error) {
        console.error('Error saving plan:', error);
        setMessages(prevMessages => [...prevMessages, { type: 'text', content: 'Error saving plan. Please try again.', isBot: true }]);
      }
      setIsLoading(false);
      return;
    }

    try {
      const chatSessionId = await sendChatMessage(message);
      setChatSessionId(chatSessionId);

      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }

      const eventSource = getChatStream(chatSessionId);
      eventSourceRef.current = eventSource;

      eventSource.onmessage = (event) => {
        if (event.data === '[DONE]') {
          setIsLoading(false);
          eventSource.close();
        } else {
          try {
            const parsedData = JSON.parse(event.data);
            setMessages(prevMessages => {
              const lastMessage = prevMessages[prevMessages.length - 1];
              if (lastMessage && lastMessage.type === parsedData.type && lastMessage.isBot) {
                const updatedMessage = {
                  ...lastMessage,
                  content: lastMessage.content + parsedData.content
                };
                return [...prevMessages.slice(0, -1), updatedMessage];
              } else {
                return [...prevMessages, { ...parsedData, isBot: true }];
              }
            });
          } catch (error) {
            console.error('Error parsing message:', error);
          }
        }
      };

      eventSource.onerror = (error) => {
        console.error('EventSource failed:', error);
        eventSource.close();
        setIsLoading(false);
      };
    } catch (error) {
      console.error('Error sending message:', error);
      setIsLoading(false);
    }
  }, [isLoading, currentPlan]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(input);
    }
  };

  const handleMenuCommand = (command: string) => {
    switch (command) {
      case 'help':
      case 'go':
      case 'clear_history':
      case 'redo':
      case 'export':
        handleSendMessage(command);
        break;
      case 'modify_code':
        setInput('modify_step_code=<step> query');
        if (textareaRef.current) {
          textareaRef.current.focus();
        }
        break;
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-900 text-white">
      <div ref={messageContainerRef} className="flex-grow overflow-y-auto p-4 space-y-4">
        {messages.map((msg, index) => (
          <ChatMessage 
            key={index} 
            type={msg.type} 
            content={msg.content} 
            isBot={msg.isBot}
            isLatest={index === messages.length - 1}
            onContentRendered={scrollToBottom}
          />
        ))}
        {isLoading && <p className="italic text-gray-500">🤖在努力思考。。。</p>}
        <div ref={messagesEndRef} />
      </div>
      <div className="flex-shrink-0 border-t border-gray-700 p-2">
        <div className="flex justify-start mb-0.5">
          <Menubar className="bg-gray-800 text-white inline-flex rounded-md">
            <MenubarMenu>
              <MenubarTrigger className="text-white px-3 py-1">命令</MenubarTrigger>
              <MenubarContent className="bg-gray-800 text-white">
                <MenubarItem onSelect={() => handleMenuCommand('help')}>帮助</MenubarItem>
                <MenubarItem onSelect={() => handleMenuCommand('go')}>执行计划</MenubarItem>
                <MenubarItem onSelect={() => handleMenuCommand('clear_history')}>清空聊天记录</MenubarItem>
                <MenubarItem onSelect={() => handleMenuCommand('modify_code')}>修改代码</MenubarItem>
                <MenubarItem onSelect={() => handleMenuCommand('redo')}>重新执行</MenubarItem>
                <MenubarSeparator />
                <MenubarItem onSelect={() => handleMenuCommand('export')}>导出</MenubarItem>
              </MenubarContent>
            </MenubarMenu>
          </Menubar>
        </div>
        <div className="flex items-center space-x-2">
          <Textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            className="flex-grow p-2 bg-gray-800 border border-gray-700 rounded-md resize-none"
            placeholder="输入消息... (Shift+Enter 换行)"
            disabled={isLoading}
            rows={1}
            style={{
              minHeight: '38px',
              maxHeight: '120px', // Approximately 5 lines
              overflow: 'auto',
            }}
          />
          <Button
            onClick={() => handleSendMessage(input)}
            className="p-2 bg-blue-600 text-white rounded-md"
            disabled={isLoading}
          >
            发送
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ChatWindow;