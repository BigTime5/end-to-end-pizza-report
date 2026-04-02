import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Users, ChevronRight } from 'lucide-react';
import type { ClientSummary } from '@/services/api';

interface ClientListProps {
  clients: ClientSummary[];
  selectedClient: string | null;
  onSelectClient: (clientId: string) => void;
}

export function ClientList({ clients, selectedClient, onSelectClient }: ClientListProps) {
  if (clients.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Users className="h-5 w-5" />
            Clients
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-zinc-500">
            No clients yet. Upload a CSV file to get started.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-lg">
          <Users className="h-5 w-5" />
          Clients ({clients.length})
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <div className="divide-y">
          {clients.map((client) => (
            <Button
              key={client.client_id}
              variant="ghost"
              className={`w-full justify-between rounded-none h-auto py-3 px-4 ${
                selectedClient === client.client_id ? 'bg-zinc-100' : ''
              }`}
              onClick={() => onSelectClient(client.client_id)}
            >
              <div className="flex flex-col items-start gap-1">
                <span className="font-medium">{client.client_id}</span>
                <div className="flex gap-1">
                  {client.tax_years.map((year) => (
                    <Badge key={year} variant="secondary" className="text-xs">
                      {year}
                    </Badge>
                  ))}
                </div>
              </div>
              <div className="flex items-center gap-2">
                {client.latest_analysis && (
                  <Badge
                    className={
                      client.latest_analysis.risk_score >= 75
                        ? 'bg-red-100 text-red-800'
                        : client.latest_analysis.risk_score >= 50
                        ? 'bg-orange-100 text-orange-800'
                        : client.latest_analysis.risk_score >= 25
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-green-100 text-green-800'
                    }
                  >
                    Risk: {client.latest_analysis.risk_score.toFixed(0)}
                  </Badge>
                )}
                <ChevronRight className="h-4 w-4 text-zinc-400" />
              </div>
            </Button>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
