import { Transaction } from "../components/TransactionItem";

export interface MockUser {
  id: string;
  name: string;
  email: string;
  phone: string;
  maskedPhone: string;
  dpi: string;
  maskedDpi: string;
  memberSince: string;
}

export interface MockAccount {
  id: string;
  accountNumber: string;
  balanceCents: number; // Centavos enteros GTQ
  currency: "GTQ";
}

export interface Beneficiary {
  id: string;
  name: string;
  phone: string;
  bank: string;
  avatarColor: string;
}

export interface BudgetCategory {
  id: string;
  name: string;
  category: "food" | "services" | "shopping" | "entertainment" | "transfer" | "other";
  spentCents: number; // Centavos enteros GTQ
  limitCents: number; // Centavos enteros GTQ
  iconName: string;
}

export const mockUser: MockUser = {
  id: "usr_99a8b7c6",
  name: "María Alejandra Morales",
  email: "m.morales@qwallet.gt",
  phone: "+502 5555-1234",
  maskedPhone: "•••• 1234", // CTRL-03
  dpi: "2489 12345 0101",
  maskedDpi: "•••• 0101", // CTRL-03
  memberSince: "Septiembre 2025",
};

export const mockAccount: MockAccount = {
  id: "acc_48291048",
  accountNumber: "•••• 8921",
  balanceCents: 1245080, // Q 12,450.80
  currency: "GTQ",
};

export const mockBeneficiaries: Beneficiary[] = [
  {
    id: "ben_1",
    name: "Carlos Gómez",
    phone: "44445678",
    bank: "Q-Wallet",
    avatarColor: "#00A86B",
  },
  {
    id: "ben_2",
    name: "Sofía Estrada",
    phone: "33339012",
    bank: "Q-Wallet",
    avatarColor: "#3B82F6",
  },
  {
    id: "ben_3",
    name: "Ferretería El Quetzal",
    phone: "22223344",
    bank: "Q-Wallet",
    avatarColor: "#8B5CF6",
  },
  {
    id: "ben_4",
    name: "Luis Fernando Castillo",
    phone: "51234567",
    bank: "Q-Wallet",
    avatarColor: "#F59E0B",
  },
];

export const mockBudgets: BudgetCategory[] = [
  {
    id: "bdg_1",
    name: "Alimentos y Supermercado",
    category: "food",
    spentCents: 185000, // Q 1,850.00
    limitCents: 250000, // Q 2,500.00
    iconName: "Utensils",
  },
  {
    id: "bdg_2",
    name: "Servicios del Hogar (Luz/Agua)",
    category: "services",
    spentCents: 95000, // Q 950.00
    limitCents: 100000, // Q 1,000.00 (95% - Advertencia)
    iconName: "Zap",
  },
  {
    id: "bdg_3",
    name: "Entretenimiento y Streaming",
    category: "entertainment",
    spentCents: 72000, // Q 720.00
    limitCents: 60000, // Q 600.00 (120% - Excedido)
    iconName: "Film",
  },
  {
    id: "bdg_4",
    name: "Compras y Ropa",
    category: "shopping",
    spentCents: 120000, // Q 1,200.00
    limitCents: 200000, // Q 2,000.00
    iconName: "ShoppingBag",
  },
];

export const mockTransactions: Transaction[] = [
  {
    id: "tx_001",
    title: "Pago de Nómina Q-Tech",
    category: "salary",
    amountCents: 850000, // +Q 8,500.00
    type: "credit",
    timestamp: "Hoy, 09:30",
    recipientOrSender: "Q-Tech Solutions, S.A.",
    status: "completed",
  },
  {
    id: "tx_002",
    title: "Supermercado La Torre",
    category: "food",
    amountCents: 43250, // -Q 432.50
    type: "debit",
    timestamp: "Hoy, 12:45",
    recipientOrSender: "Terminal POS Cayalá",
    status: "completed",
  },
  {
    id: "tx_003",
    title: "Transferencia a Carlos Gómez",
    category: "transfer",
    amountCents: 15000, // -Q 150.00
    type: "debit",
    timestamp: "Ayer, 18:20",
    recipientOrSender: "Tel: •••• 5678",
    status: "completed",
  },
  {
    id: "tx_004",
    title: "Pago Empresa Eléctrica EEGSA",
    category: "services",
    amountCents: 38000, // -Q 380.00
    type: "debit",
    timestamp: "01 Oct, 14:10",
    recipientOrSender: "Servicio No. 902184",
    status: "completed",
  },
  {
    id: "tx_005",
    title: "Transferencia de Sofía Estrada",
    category: "transfer",
    amountCents: 27500, // +Q 275.00
    type: "credit",
    timestamp: "30 Sep, 20:00",
    recipientOrSender: "Almuerzo reunión",
    status: "completed",
  },
  {
    id: "tx_006",
    title: "Suscripción Netflix",
    category: "entertainment",
    amountCents: 9900, // -Q 99.00
    type: "debit",
    timestamp: "28 Sep, 02:00",
    recipientOrSender: "Débito automático",
    status: "completed",
  },
  {
    id: "tx_007",
    title: "Farmacias Galeno",
    category: "shopping",
    amountCents: 14500, // -Q 145.00
    type: "debit",
    timestamp: "27 Sep, 16:30",
    recipientOrSender: "POS Zona 10",
    status: "completed",
  },
  {
    id: "tx_008",
    title: "Café Barista",
    category: "food",
    amountCents: 3800, // -Q 38.00
    type: "debit",
    timestamp: "26 Sep, 08:15",
    recipientOrSender: "Diagonal 6",
    status: "completed",
  },
  {
    id: "tx_009",
    title: "Gasolina Shell Las Américas",
    category: "services",
    amountCents: 35000, // -Q 350.00
    type: "debit",
    timestamp: "25 Sep, 19:40",
    recipientOrSender: "Estación 044",
    status: "completed",
  },
  {
    id: "tx_010",
    title: "Transferencia a Ferretería",
    category: "transfer",
    amountCents: 52000, // -Q 520.00
    type: "debit",
    timestamp: "24 Sep, 11:25",
    recipientOrSender: "Materiales",
    status: "completed",
  },
];
