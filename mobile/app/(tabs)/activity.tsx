import React, { useState, useMemo } from "react";
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  ScrollView,
} from "react-native";
import { Search, Filter, RefreshCw, FileText } from "lucide-react-native";
import { useTheme } from "../../src/theme";
import {
  Header,
  Input,
  TransactionItem,
  EmptyState,
  Skeleton,
  Card,
} from "../../src/components";
import { mockTransactions } from "../../src/mocks";
import { Transaction } from "../../src/components/TransactionItem";

type FilterType = "all" | "credit" | "debit";

// Simulación de paginación con tope máximo de 50 elementos (CTRL-05)
const MAX_PAGINATION_LIMIT = 50;

export default function ActivityScreen() {
  const { colors, palette, isDark } = useTheme();

  const [searchQuery, setSearchQuery] = useState("");
  const [filterType, setFilterType] = useState<FilterType>("all");
  const [categoryFilter, setCategoryFilter] = useState<string>("all");
  const [isLoading, setIsLoading] = useState(false);
  const [displayedCount, setDisplayedCount] = useState(10);

  // Generamos transacciones adicionales para demostrar paginación hasta el tope de 50 (CTRL-05)
  const allGeneratedTransactions: Transaction[] = useMemo(() => {
    const list: Transaction[] = [...mockTransactions];
    // Duplicar con IDs únicos para llegar a ~30 elementos dentro del tope de 50
    for (let i = 1; i <= 2; i++) {
      mockTransactions.forEach((tx, idx) => {
        list.push({
          ...tx,
          id: `tx_gen_${i}_${idx}`,
          timestamp: `${20 - idx} Sep, 10:00`,
        });
      });
    }
    // Límite estricto de seguridad: tope de 50 (CTRL-05)
    return list.slice(0, MAX_PAGINATION_LIMIT);
  }, []);

  const filteredTransactions = useMemo(() => {
    return allGeneratedTransactions.filter((tx) => {
      // Filtro tipo
      if (filterType === "credit" && tx.type !== "credit") return false;
      if (filterType === "debit" && tx.type !== "debit") return false;

      // Filtro categoría
      if (categoryFilter !== "all" && tx.category !== categoryFilter)
        return false;

      // Filtro búsqueda
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        const matchTitle = tx.title.toLowerCase().includes(query);
        const matchSub = tx.recipientOrSender?.toLowerCase().includes(query);
        return matchTitle || matchSub;
      }

      return true;
    });
  }, [allGeneratedTransactions, filterType, categoryFilter, searchQuery]);

  const visibleTransactions = filteredTransactions.slice(0, displayedCount);

  // TODO(CTRL-05): Paginación por cursor hacia GET /accounts/{accountId}/transactions con tope máximo limit=50
  const handleLoadMore = () => {
    if (displayedCount < filteredTransactions.length && displayedCount < MAX_PAGINATION_LIMIT) {
      setIsLoading(true);
      setTimeout(() => {
        setDisplayedCount((prev) => Math.min(prev + 10, MAX_PAGINATION_LIMIT));
        setIsLoading(false);
      }, 500);
    }
  };

  const categories = [
    { id: "all", label: "Todas" },
    { id: "food", label: "Comida" },
    { id: "transfer", label: "Transferencias" },
    { id: "services", label: "Servicios" },
    { id: "shopping", label: "Compras" },
    { id: "salary", label: "Salario" },
  ];

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      <Header title="Historial de Movimientos" />

      <View style={styles.searchSection}>
        <Input
          placeholder="Buscar por comercio o destinatario..."
          value={searchQuery}
          onChangeText={setSearchQuery}
          leftIcon={<Search size={18} color={colors.textMuted} />}
          containerStyle={{ marginBottom: 10 }}
        />

        {/* Tipo: Todos / Ingresos / Gastos */}
        <View style={styles.typeTabsRow}>
          <TouchableOpacity
            onPress={() => setFilterType("all")}
            style={[
              styles.typeTab,
              filterType === "all" && {
                backgroundColor: palette.accent,
              },
            ]}
          >
            <Text
              style={[
                styles.typeTabText,
                { color: filterType === "all" ? "#FFFFFF" : colors.textMuted },
              ]}
            >
              Todos
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            onPress={() => setFilterType("credit")}
            style={[
              styles.typeTab,
              filterType === "credit" && {
                backgroundColor: palette.accent,
              },
            ]}
          >
            <Text
              style={[
                styles.typeTabText,
                { color: filterType === "credit" ? "#FFFFFF" : colors.textMuted },
              ]}
            >
              Ingresos (+)
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            onPress={() => setFilterType("debit")}
            style={[
              styles.typeTab,
              filterType === "debit" && {
                backgroundColor: palette.accent,
              },
            ]}
          >
            <Text
              style={[
                styles.typeTabText,
                { color: filterType === "debit" ? "#FFFFFF" : colors.textMuted },
              ]}
            >
              Gastos (-)
            </Text>
          </TouchableOpacity>
        </View>

        {/* Categorías chips */}
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.categoryChips}
        >
          {categories.map((c) => (
            <TouchableOpacity
              key={c.id}
              onPress={() => setCategoryFilter(c.id)}
              style={[
                styles.chip,
                {
                  backgroundColor:
                    categoryFilter === c.id
                      ? isDark
                        ? colors.surfaceSubtle
                        : palette.gray[200]
                      : "transparent",
                  borderColor:
                    categoryFilter === c.id
                      ? palette.accent
                      : colors.border,
                },
              ]}
            >
              <Text
                style={[
                  styles.chipText,
                  {
                    color:
                      categoryFilter === c.id
                        ? palette.accent
                        : colors.textMuted,
                  },
                ]}
              >
                {c.label}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      {/* Transaction List */}
      <FlatList
        data={visibleTransactions}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => <TransactionItem transaction={item} />}
        contentContainerStyle={styles.listContent}
        showsVerticalScrollIndicator={false}
        ListEmptyComponent={
          <EmptyState
            icon={<FileText size={40} color={palette.accent} />}
            title="Sin movimientos coincidentes"
            description="No se encontraron transacciones con los filtros seleccionados."
            actionTitle="Restablecer filtros"
            onAction={() => {
              setSearchQuery("");
              setFilterType("all");
              setCategoryFilter("all");
            }}
          />
        }
        ListFooterComponent={
          isLoading ? (
            <View style={styles.loadingFooter}>
              <Skeleton height={50} borderRadius={14} style={{ marginBottom: 8 }} />
              <Skeleton height={50} borderRadius={14} />
            </View>
          ) : displayedCount < filteredTransactions.length &&
            displayedCount < MAX_PAGINATION_LIMIT ? (
            <TouchableOpacity
              onPress={handleLoadMore}
              style={[
                styles.loadMoreButton,
                { backgroundColor: colors.card, borderColor: colors.cardBorder },
              ]}
            >
              <RefreshCw size={16} color={palette.accent} />
              <Text style={[styles.loadMoreText, { color: palette.accent }]}>
                Cargar más (tope de 50 - CTRL-05)
              </Text>
            </TouchableOpacity>
          ) : visibleTransactions.length > 0 ? (
            <Text style={[styles.endText, { color: colors.textSubtle }]}>
              Tope de 50 movimientos por consulta (CTRL-05)
            </Text>
          ) : null
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  searchSection: {
    paddingHorizontal: 20,
    paddingTop: 8,
    paddingBottom: 12,
  },
  typeTabsRow: {
    flexDirection: "row",
    gap: 8,
    marginBottom: 10,
  },
  typeTab: {
    flex: 1,
    paddingVertical: 8,
    borderRadius: 10,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "rgba(148, 163, 184, 0.15)",
  },
  typeTabText: {
    fontSize: 13,
    fontFamily: "Inter_600SemiBold",
  },
  categoryChips: {
    gap: 8,
    paddingVertical: 4,
  },
  chip: {
    paddingVertical: 6,
    paddingHorizontal: 14,
    borderRadius: 20,
    borderWidth: 1,
  },
  chipText: {
    fontSize: 12,
    fontFamily: "Inter_500Medium",
  },
  listContent: {
    paddingHorizontal: 20,
    paddingBottom: 32,
    gap: 4,
  },
  loadingFooter: {
    paddingVertical: 12,
  },
  loadMoreButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: 12,
    borderRadius: 12,
    borderWidth: 1,
    gap: 8,
    marginVertical: 14,
  },
  loadMoreText: {
    fontSize: 13,
    fontFamily: "Inter_600SemiBold",
  },
  endText: {
    textAlign: "center",
    fontSize: 11,
    fontFamily: "Inter_400Regular",
    marginVertical: 16,
  },
});
