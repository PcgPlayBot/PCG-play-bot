const Body = () => {

    const language = useLanguage()
    const spawnText = language.SPAWN
    const capturedText = language.CAPTURED
    const pokedexText = language.POKEDEX
    const inventoryText = language.INVENTORY
    const missionsText = language.MISSIONS

    const lastSpawn = ReactRedux.useSelector(state => state.lastSpawn);
    const pokemonData = ReactRedux.useSelector(state => state.pokemonData);

    const [countdown, setCountdown] = React.useState("00:00");

    React.useEffect(() => {

        const FIFTEEN_MINUTES = 15 * 60 * 1000

        if (lastSpawn.datetime == null || new Date() - new Date(lastSpawn.datetime) >= FIFTEEN_MINUTES) {
            setCountdown("00:00");
            return;
        }

        const intervalId = setInterval(() => {
            const elapsedTime = Math.floor((new Date() - new Date(lastSpawn.datetime)) / 1000);
            const remainingTime = Math.max(15 * 60 - elapsedTime, 0);

            const minutes = Math.floor(remainingTime / 60);
            const seconds = remainingTime % 60;

            setCountdown(`${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`);

            if (remainingTime === 0) {
                clearInterval(intervalId);
            }
        }, 1000);

        return () => clearInterval(intervalId);
    }, [lastSpawn]);

    const renderInventoryContent = () => {

        const inventory = []

        inventory.push(
            <div className={"list-item"} key={0}>
                <p className={"page-text"}>
                    {inventoryText.CASH}
                    <strong>${pokemonData.inventory.cash}</strong>
                </p>
            </div>
        )

        pokemonData.inventory.items.forEach((item, key) => {
            inventory.push(
                <div className={"list-item"} key={key + 1}>
                    <p className={"page-text list-item-spacing"}>{item.name}</p>
                    <p className={"page-text page-text-bold"}>{item.amount}</p>
                </div>
            )
        })

        return inventory
    }

    const renderMissionsContent = () => {

        const inventory = []

        if (pokemonData.missions.end_date !== "") {
            inventory.push(
                <div className={"list-item"} key={0}>
                    <p className={"page-text"}>
                        {missionsText.TIME}
                        <strong>{pokemonData.missions.end_date}</strong>
                    </p>
                </div>
            )
        }

        pokemonData.missions.missions.forEach((mission, key) => {
            inventory.push(
                <div className={"list-item"} key={key + 1}>
                    <p className={"page-text list-item-spacing"}>{mission.name}</p>
                    <div>
                        <p className={"page-text page-text-bold"}>
                            {mission.progress <= mission.goal ? mission.progress : mission.goal}/{mission.goal}
                        </p>
                    </div>
                </div>
            )
        })

        return inventory
    }

    return (
        <div className={"body-container"}>

            <div className={"spawn-container"}>

                <p className={"body-text-tile"}>{spawnText.TITLE}</p>

                <div className={"poke-data-container"}>
                    <p className={"page-text"}>
                        {spawnText.TIMER}
                        <strong>{countdown}</strong>
                    </p>

                    {lastSpawn.name !== "" &&
                        <p className={"page-text"}>
                            {spawnText.LAST}
                            <strong>{lastSpawn.name}</strong>
                        </p>
                    }
                </div>

            </div>

            <div>
                <p className={"body-text-tile"}>{capturedText.TITLE}</p>

                <div className={"poke-data-container"}>
                    <p className={"page-text"}>
                        {capturedText.TOTAL}
                        <strong>{pokemonData.captured.total_count}</strong>
                    </p>
                    <p className={"page-text"}>
                        {capturedText.UNIQUE}
                        <strong>{pokemonData.captured.unique_count}</strong>
                    </p>
                    <p className={"page-text"}>
                        {capturedText.SHINY}
                        <strong>{pokemonData.captured.shiny_count}</strong>
                    </p>
                </div>

                <div className={"poke-data-container poke-data-pokedex"}>
                    <p className={"page-text"}>
                        {pokedexText.TOTAL}
                        <strong>{pokemonData.pokedex.total_progress}/{pokemonData.pokedex.total_count} ({calculatePokedexCompletion(pokemonData.pokedex.total_progress, pokemonData.pokedex.total_count)}%)</strong>
                    </p>
                    <p className={"page-text"}>
                        {pokedexText.SPAWN}
                        <strong>{pokemonData.pokedex.spawn_progress}/{pokemonData.pokedex.spawn_count} ({calculatePokedexCompletion(pokemonData.pokedex.spawn_progress, pokemonData.pokedex.spawn_count)}%)</strong>
                    </p>
                </div>

            </div>

            <div className={"lists-container"}>

                <div className={"list-container"}>
                    <p className={"body-text-tile list-title"}>{inventoryText.TITLE}</p>
                    <div className={"list"}>
                        {renderInventoryContent()}
                    </div>
                </div>

                <div className={"list-container"}>
                    <p className={"body-text-tile list-title"}>{missionsText.TITLE}</p>
                    <div className={"list"}>
                        {renderMissionsContent()}
                    </div>
                </div>

            </div>

        </div>
    );
}


const calculatePokedexCompletion = (progress, count) => {
    if (count === 0) return 0
    else return (progress / count * 100).toFixed(1)
}
