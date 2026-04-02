import { useState, useEffect, useCallback } from 'react';
import { Shield, RefreshCw } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { FileUpload } from '@/components/FileUpload';
import { PlaidConnect } from '@/components/PlaidConnect';
import { ClientList } from '@/components/ClientList';
import { AnalysisDashboard } from '@/components/AnalysisDashboard';
import {
  getClients,
  getClient,
  type ClientSummary,
  type UploadResponse,
} from '@/services/api';

function App() {
  const [clients, setClients] = useState<ClientSummary[]>([]);
  const [selectedClient, setSelectedClient] = useState<ClientSummary | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const loadClients = useCallback(async () => {
    try {
      const data = await getClients();
      setClients(data);
    } catch {
      // silently fail on initial load
    }
  }, []);

  useEffect(() => {
    loadClients();
  }, [loadClients]);

  const handleUploadSuccess = async (result: UploadResponse) => {
    await loadClients();
    try {
      const client = await getClient(result.client_id);
      setSelectedClient(client);
    } catch {
      // fall back to refreshing list
    }
  };

  const handleSelectClient = async (clientId: string) => {
    try {
      const client = await getClient(clientId);
      setSelectedClient(client);
    } catch {
      const found = clients.find((c) => c.client_id === clientId);
      if (found) setSelectedClient(found);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadClients();
    if (selectedClient) {
      try {
        const updated = await getClient(selectedClient.client_id);
        setSelectedClient(updated);
      } catch {
        // keep current
      }
    }
    setRefreshing(false);
  };

  return (
    <div className="min-h-screen bg-zinc-50">
      {/* Header */}
      <header className="bg-white border-b border-zinc-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="bg-indigo-600 p-2 rounded-lg">
                <Shield className="h-5 w-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold text-zinc-900">TaxGuard AI</h1>
                <p className="text-xs text-zinc-500">Anomaly Detection for CPAs</p>
              </div>
            </div>
            <Button variant="ghost" size="sm" onClick={handleRefresh} disabled={refreshing}>
              <RefreshCw className={`h-4 w-4 mr-1 ${refreshing ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left sidebar */}
          <div className="lg:col-span-3 space-y-6">
            <Tabs defaultValue="upload">
              <TabsList className="w-full">
                <TabsTrigger value="upload" className="flex-1">CSV Upload</TabsTrigger>
                <TabsTrigger value="plaid" className="flex-1">Plaid</TabsTrigger>
              </TabsList>
              <TabsContent value="upload" className="mt-4">
                <FileUpload onUploadSuccess={handleUploadSuccess} />
              </TabsContent>
              <TabsContent value="plaid" className="mt-4">
                <PlaidConnect />
              </TabsContent>
            </Tabs>

            <ClientList
              clients={clients}
              selectedClient={selectedClient?.client_id ?? null}
              onSelectClient={handleSelectClient}
            />
          </div>

          {/* Main area */}
          <div className="lg:col-span-9">
            {selectedClient ? (
              <AnalysisDashboard client={selectedClient} />
            ) : (
              <div className="bg-white rounded-xl border border-zinc-200 p-12 text-center">
                <Shield className="h-16 w-16 mx-auto mb-4 text-zinc-200" />
                <h2 className="text-xl font-semibold text-zinc-700 mb-2">
                  Welcome to TaxGuard AI
                </h2>
                <p className="text-zinc-500 max-w-md mx-auto mb-6">
                  Upload client financial data via CSV or connect through Plaid to
                  start detecting tax anomalies with AI-powered analysis.
                </p>
                <div className="flex flex-col gap-3 max-w-xs mx-auto text-left">
                  <div className="flex items-start gap-3">
                    <span className="bg-indigo-100 text-indigo-700 rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold shrink-0">1</span>
                    <span className="text-sm text-zinc-600">Upload a CSV with client financial data</span>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="bg-indigo-100 text-indigo-700 rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold shrink-0">2</span>
                    <span className="text-sm text-zinc-600">Select a client and run anomaly detection</span>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="bg-indigo-100 text-indigo-700 rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold shrink-0">3</span>
                    <span className="text-sm text-zinc-600">Review flagged items and export PDF reports</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
