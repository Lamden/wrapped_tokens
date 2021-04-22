const Migrations = artifacts.require("Migrations");
const MintableToken = artifacts.require("MintableToken");

module.exports = function(deployer) {
  deployer.deploy(Migrations);
  deployer.deploy(MintableToken);
};
