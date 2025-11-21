export const useCredit = () => {
    const credits = useState<number>('user-credits', () => 3450);

    const addCredits = (amount: number) => {
        credits.value += amount;
    };

    const subtractCredits = (amount: number) => {
        if (credits.value >= amount) {
            credits.value -= amount;
            return true;
        }
        return false;
    };

    const setCredits = (amount: number) => {
        credits.value = amount;
    };

    return {
        credits,
        addCredits,
        subtractCredits,
        setCredits
    };
}