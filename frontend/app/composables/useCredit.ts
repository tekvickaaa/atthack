export const useCredit = () => {
    const credits = useState<number>('user-credits', () => 3450);
    const userData = useState<any>('user-data', () => null);

    const fetchCredits = async () => {
        try {
            const response = await $fetch<any>('/api/user/alice');
            if (response) {
                userData.value = response;
                if (typeof response.credits === 'number') {
                    credits.value = response.credits;
                }
            }
        } catch (error) {
            console.error('Failed to fetch credits:', error);
        }
    };

    const updateRemoteCredits = async (newCredits: number) => {
        if (!userData.value) return;
        
        const updatedUser = {
            ...userData.value,
            credits: newCredits
        };

        try {
            await $fetch('/api/user/alice', {
                method: 'PUT',
                body: updatedUser
            });
            userData.value = updatedUser;
        } catch (error) {
            console.error('Failed to update credits:', error);
        }
    };

    const addCredits = async (amount: number) => {
        credits.value += amount;
        await updateRemoteCredits(credits.value);
    };

    const subtractCredits = async (amount: number) => {
        if (credits.value >= amount) {
            credits.value -= amount;
            await updateRemoteCredits(credits.value);
            return true;
        }
        return false;
    };

    const setCredits = async (amount: number) => {
        credits.value = amount;
        await updateRemoteCredits(credits.value);
    };

    return {
        credits,
        fetchCredits,
        addCredits,
        subtractCredits,
        setCredits
    };
}