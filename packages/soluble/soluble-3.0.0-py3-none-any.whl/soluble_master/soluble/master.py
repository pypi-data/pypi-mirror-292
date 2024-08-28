async def setup(hub, name: str):
    """Setup the ephemeral master using raw Salt execution modules."""
    config = hub.soluble.RUN[name]

    # Copy the master config to the target
    master_config = hub.lib.path.Path(config.master_config)

    if master_config.exists():
        hub.log.info("Copying master configuration to target(s)...")
        await hub.salt.ssh.run_command(
            name,
            f"state.single file.managed source=file://{config.master_config} name=/etc/salt/master",
        )

    # Install Salt on the target
    hub.log.info("Installing Salt on target(s)...")
    await hub.salt.ssh.run_command(name, "state.single pkg.installed name=salt-master")

    # Start the Salt master service
    hub.log.info("Starting salt-master service on target(s)...")
    await hub.salt.ssh.run_command(
        name, "state.single service.running name=salt-master"
    )

    # Enable the service to start on boot
    await hub.salt.ssh.run_command(name, "service.enabled name=salt-master")


async def run(hub, name: str) -> int:
    """
    Run the master until a keyboard interrupt is received on the host
    """
    try:
        while True:
            await hub.lib.asyncio.sleep(1)
    except KeyboardInterrupt:
        hub.log.info(f"Received keyboard interrupt, tearing down salt master")

    return 0


async def teardown(hub, name: str):
    """Teardown the ephemeral master using raw Salt execution modules."""
    # Stop the Salt master service
    hub.log.info("Stopping salt-master service on target(s)...")
    await hub.salt.ssh.run_command(
        name, "state.single service.disabled name=salt-master"
    )
    await hub.salt.ssh.run_command(name, "state.single service.dead name=salt-master")

    # Uninstall Salt from the target
    hub.log.info("Uninstalling Salt from target(s)...")
    await hub.salt.ssh.run_command(name, "state.single pkg.removed name=salt-master")

    # Remove the master configuration file
    hub.log.info("Removing master configuration from target(s)...")
    await hub.salt.ssh.run_command(
        name, "state.single file.absent name=/etc/salt/master"
    )
