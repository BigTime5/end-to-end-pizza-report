import { useState } from 'react';
import { Landmark, CheckCircle2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  createPlaidLinkToken,
  exchangePlaidToken,
  getPlaidTransactions,
  type PlaidTransaction,
} from '@/services/api';

interface PlaidConnectProps {
  onTransactionsLoaded?: (clientId: string, transactions: PlaidTransaction[]) => void;
}

export function PlaidConnect({ onTransactionsLoaded }: PlaidConnectProps) {
  const [clientId, setClientId] = useState('');
  const [connecting, setConnecting] = useState(false);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [transactionCount, setTransactionCount] = useState(0);

  const handleConnect = async () => {
    if (!clientId.trim()) {
      setError('Please enter a client ID');
      return;
    }

    setConnecting(true);
    setError(null);

    try {
      const linkToken = await createPlaidLinkToken();
      await exchangePlaidToken(linkToken.link_token, clientId);
      const txns = await getPlaidTransactions(clientId);
      setTransactionCount(txns.total_count);
      setConnected(true);
      onTransactionsLoaded?.(clientId, txns.transactions);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Connection failed');
    } finally {
      setConnecting(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Landmark className="h-5 w-5" />
          Connect via Plaid
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm text-zinc-500">
          Connect a client's bank account to automatically import financial data.
          <span className="block text-xs mt-1 text-zinc-400">
            (Sandbox mode - uses mock data for demo)
          </span>
        </p>

        <div className="space-y-2">
          <Label htmlFor="plaid-client-id">Client ID</Label>
          <div className="flex gap-2">
            <Input
              id="plaid-client-id"
              placeholder="e.g., CLIENT-001"
              value={clientId}
              onChange={(e) => setClientId(e.target.value)}
              disabled={connected}
            />
            <Button
              onClick={handleConnect}
              disabled={connecting || connected}
              variant={connected ? 'outline' : 'default'}
            >
              {connecting ? 'Connecting...' : connected ? 'Connected' : 'Connect'}
            </Button>
          </div>
        </div>

        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {connected && (
          <Alert>
            <CheckCircle2 className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800">
              Connected successfully. Loaded {transactionCount} transactions for {clientId}.
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
}
