'use client';

import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { getSession, updateCurrentPlan, updateStepCodes, getSSEStream } from '@/lib/api';
import '../styles/custom-tabs.css';

const ChatWindow = dynamic(() => import('@/components/ChatWindow'), { ssr: false });
const MainWindow = dynamic(() => import('@/components/MainWindow'), { ssr: false });

interface SessionData {
  session_id: string;
  chat_history: any[];
  current_plan: any;
  step_codes: { [key: string]: string };
}

const Home: React.FC = () => {
  const [sessionData, setSessionData] = useState<SessionData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSessionData = async () => {
      try {
        const data = await getSession();
        setSessionData(data);
        // Open SSE connection
        const eventSource = getSSEStream(data.session_id);
        eventSource.onmessage = (event) => {
          const parsedData = JSON.parse(event.data);
          if (parsedData.type === 'chat_history') {
            setSessionData(prevData => ({
              ...prevData!,
              chat_history: parsedData.chat_history
            }));
          } else if (parsedData.type === 'plan') {
            setSessionData(prevData => ({
              ...prevData!,
              current_plan: parsedData.plan
            }));
          } else if (parsedData.type === 'code') {
            setSessionData(prevData => ({
              ...prevData!,
              step_codes: parsedData.step_codes
            }));
          }
        };
        eventSource.onerror = (error) => {
          console.error('EventSource failed:', error);
          eventSource.close();
        };
      } catch (error) {
        console.error('Failed to fetch session data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchSessionData();
  }, []);

  const handlePlanUpdate = async (newPlan: any) => {
    if (!sessionData) return;
    try {
      await updateCurrentPlan(newPlan);
      setSessionData(prevData => ({
        ...prevData!,
        current_plan: newPlan
      }));
    } catch (error) {
      console.error('Failed to update plan:', error);
    }
  };

  const handleCodeUpdate = async (step: string, newCode: string) => {
    if (!sessionData) return;
    try {
      const updatedStepCodes = {
        ...sessionData.step_codes,
        [step]: newCode
      };
      await updateStepCodes(updatedStepCodes);
      setSessionData(prevData => ({
        ...prevData!,
        step_codes: updatedStepCodes
      }));
    } catch (error) {
      console.error('Failed to update code:', error);
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-screen bg-background text-foreground">Loading...</div>;
  }

  if (!sessionData) {
    return <div className="flex justify-center items-center h-screen bg-background text-foreground">No session data available.</div>;
  }

  return (
    <div className="flex h-screen w-full bg-background text-foreground overflow-hidden">
      <div className="w-1/4 border-r border-border overflow-hidden">
        <ChatWindow initialMessages={sessionData.chat_history} />
      </div>
      <div className="w-3/4 overflow-hidden">
        <MainWindow
          currentPlan={sessionData.current_plan}
          stepCodes={sessionData.step_codes}
          onPlanUpdate={handlePlanUpdate}
          onCodeUpdate={handleCodeUpdate}
        />
      </div>
    </div>
  );
};

export default Home;
