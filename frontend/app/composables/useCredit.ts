export const useCredit = () => {
    const credits = useState<number>('user-credits', () => 0);
    const userData = useState<any>('user-data', () => null);

    const fetchCredits = async () => {
        try {
            console.log('Fetching credits for alice...');
            const response = await $fetch<any>('/api/user/alice');
            console.log('Fetch response:', response);
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
        if (!userData.value) {
            console.log('userData is null, trying to fetch...');
            await fetchCredits();
            if (!userData.value) {
                console.error('Cannot update remote credits: userData is still null');
                return;
            }
        }
        
        const updatedUser = {
            ...userData.value,
            credits: newCredits
        };

        console.log('Updating remote credits:', updatedUser);

        try {
            const result = await $fetch('/api/user/alice', {
                method: 'PUT',
                body: updatedUser
            });
            console.log('Update result:', result);
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