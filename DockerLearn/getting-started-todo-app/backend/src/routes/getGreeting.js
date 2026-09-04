const GREETING = 'Hello there!';

module.exports = async (req, res) => {
    res.send({
        greeting: GREETING,
    });
};
