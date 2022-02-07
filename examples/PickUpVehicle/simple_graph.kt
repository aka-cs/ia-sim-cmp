fun main(): Void{
    var a = PickUpVehicle(1, "A");

    var edges = {"A": {"B": 5},
                    "B": {"A": 5, "C": 4, "D": 1000},
                    "C": {"B": 4, "D": 1},
                    "D": {"B": 1, "C": 5}};
    var env = GraphEnvironment(edges, {"A": {1: a},
                                        "B": {3: MapObject(3, "B")},
                                        "C": {2: MapObject(2, "C")},
                                        "D": {4: MapObject(4, "D")}});
    simulate_environment(env, [Event(0, 1)], 1000);
}