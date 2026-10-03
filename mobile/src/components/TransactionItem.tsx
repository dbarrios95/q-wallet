import React from "react";
import { View, Text, StyleSheet, TouchableOpacity } from "react-native";
import {
  ArrowDownLeft,
  ArrowUpRight,
  ShoppingBag,
  Utensils,
  Zap,
  Film,
  Briefcase,
  HelpCircle,
} from "lucide-react-native";
import { useTheme } from "../theme";
import { formatGTQ } from "./BalanceCard";

export interface Transaction {
  id: string;
  title: string;
  category: "transfer" | "shopping" | "food" | "services" | "entertainment" | "salary" | "other";
  amountCents: number;
  type: "credit" | "debit";
  timestamp: string; // ISO date or formatted
  recipientOrSender?: string;
  status?: "completed" | "pending" | "failed";
}

export interface TransactionItemProps {
  transaction: Transaction;
  onPress?: () => void;
}

export const TransactionItem: React.FC<TransactionItemProps> = ({
  transaction,
  onPress,
}) => {
  const { colors, palette, isDark } = useTheme();

  const isCredit = transaction.type === "credit";

  // Category Icon & colors
  const getCategoryConfig = () => {
    switch (transaction.category) {
      case "salary":
        return {
          icon: <Briefcase size={18} color="#00A86B" />,
          bg: isDark ? "#082B1E" : "#E6F7F0",
        };
      case "transfer":
        return {
          icon: isCredit ? (
            <ArrowDownLeft size={18} color="#00A86B" />
          ) : (
            <ArrowUpRight size={18} color="#3B82F6" />
          ),
          bg: isCredit
            ? isDark
              ? "#082B1E"
              : "#E6F7F0"
            : isDark
            ? "#0F2445"
            : "#EFF6FF",
        };
      case "food":
        return {
          icon: <Utensils size={18} color="#F59E0B" />,
          bg: isDark ? "#322307" : "#FEF3C7",
        };
      case "shopping":
        return {
          icon: <ShoppingBag size={18} color="#8B5CF6" />,
          bg: isDark ? "#2A184D" : "#F3E8FF",
        };
      case "services":
        return {
          icon: <Zap size={18} color="#EC4899" />,
          bg: isDark ? "#3A1127" : "#FCE7F3",
        };
      case "entertainment":
        return {
          icon: <Film size={18} color="#06B6D4" />,
          bg: isDark ? "#0A2932" : "#CFFAFE",
        };
      default:
        return {
          icon: <HelpCircle size={18} color="#64748B" />,
          bg: isDark ? "#1E293B" : "#F1F5F9",
        };
    }
  };

  const cat = getCategoryConfig();

  return (
    <TouchableOpacity
      onPress={onPress}
      disabled={!onPress}
      activeOpacity={0.7}
      style={[
        styles.container,
        {
          backgroundColor: colors.card,
          borderColor: colors.cardBorder,
        },
      ]}
    >
      <View style={[styles.iconContainer, { backgroundColor: cat.bg }]}>
        {cat.icon}
      </View>

      <View style={styles.detailsContainer}>
        <Text style={[styles.title, { color: colors.text }]} numberOfLines={1}>
          {transaction.title}
        </Text>
        <Text style={[styles.subtitle, { color: colors.textMuted }]}>
          {transaction.recipientOrSender || transaction.timestamp}
        </Text>
      </View>

      <View style={styles.amountContainer}>
        <Text
          style={[
            styles.amountText,
            {
              color: isCredit ? palette.accent : colors.text,
            },
          ]}
        >
          {isCredit ? "+" : "-"}
          {formatGTQ(transaction.amountCents)}
        </Text>
        <Text style={[styles.dateText, { color: colors.textSubtle }]}>
          {transaction.timestamp}
        </Text>
      </View>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 14,
    marginVertical: 4,
  },
  iconContainer: {
    width: 42,
    height: 42,
    borderRadius: 12,
    alignItems: "center",
    justifyContent: "center",
    marginRight: 12,
  },
  detailsContainer: {
    flex: 1,
    justifyContent: "center",
  },
  title: {
    fontSize: 15,
    fontFamily: "Inter_600SemiBold",
  },
  subtitle: {
    fontSize: 12,
    fontFamily: "Inter_400Regular",
    marginTop: 2,
  },
  amountContainer: {
    alignItems: "flex-end",
  },
  amountText: {
    fontSize: 15,
    fontFamily: "Inter_600SemiBold",
  },
  dateText: {
    fontSize: 11,
    fontFamily: "Inter_400Regular",
    marginTop: 2,
  },
});
